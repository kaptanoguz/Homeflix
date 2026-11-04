package com.kaptanoguz.homeflix.tv;

import android.app.Activity;
import android.app.AlertDialog;
import android.content.SharedPreferences;
import android.graphics.Bitmap;
import android.graphics.Color;
import android.net.Uri;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.InputType;
import android.view.KeyEvent;
import android.view.Gravity;
import android.view.View;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.EditText;
import android.widget.FrameLayout;
import android.widget.TextView;
import android.widget.Toast;

import org.json.JSONObject;

import java.io.ByteArrayOutputStream;
import java.io.InputStream;
import java.net.DatagramPacket;
import java.net.DatagramSocket;
import java.net.InetAddress;
import java.net.InterfaceAddress;
import java.net.NetworkInterface;
import java.net.SocketTimeoutException;
import java.util.ArrayList;
import java.util.Collections;
import java.util.LinkedHashSet;
import java.util.List;
import java.util.Set;
import java.nio.charset.StandardCharsets;

public class MainActivity extends Activity {

    private static final String PREFS = "homeflix_tv";
    private static final String KEY_URL = "server_url";

    private FrameLayout root;
    private WebView web;
    private View customView;
    private WebChromeClient.CustomViewCallback customCallback;
    private WebChromeClient chrome;
    private AlertDialog dialog;
    private String navJs = "";
    private final Handler handler = new Handler(Looper.getMainLooper());
    private final Runnable retry = () -> load(currentUrl());
    private TextView offlineView;
    private boolean offline;
    private boolean loadFailed;

    private static final int RETRY_MS = 5000;
    private static final String ADDRESS_HINT = "Bilgisayarın adresini girin (örn. 10.1.5.74:5000)";
    // Homeflix sunucusu bu UDP portundaki soruya adresiyle cevap verir (homeflix/discovery.py).
    private static final int DISCOVERY_PORT = 5099;
    private static final String DISCOVER_QUERY = "HOMEFLIX_DISCOVER";
    private volatile boolean discovering;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);

        root = new FrameLayout(this);
        root.setBackgroundColor(Color.BLACK);
        web = new WebView(this);
        root.addView(web, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));
        offlineView = new TextView(this);
        offlineView.setBackgroundColor(Color.parseColor("#0b0b0f"));
        offlineView.setTextColor(Color.parseColor("#f5f5f7"));
        offlineView.setTextSize(20);
        offlineView.setGravity(Gravity.CENTER);
        offlineView.setPadding(48, 0, 48, 0);
        offlineView.setVisibility(View.GONE);
        // Telefonda kumanda yok: bağlantı ekranına dokunmak adres penceresini açar.
        offlineView.setOnClickListener(v -> showAddressDialog(ADDRESS_HINT));
        root.addView(offlineView, new FrameLayout.LayoutParams(
                FrameLayout.LayoutParams.MATCH_PARENT,
                FrameLayout.LayoutParams.MATCH_PARENT));
        setContentView(root);

        navJs = readAsset("tv-nav.js");
        setupWebView();
        // İlk açılışta sunucu ağda aranır; bulunamazsa adres sorulur. Sonra kayıtlı adres kullanılır.
        if (hasSavedUrl()) load(currentUrl());
        else findOnFirstLaunch();
    }

    private void setupWebView() {
        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_ALWAYS_ALLOW);
        s.setUserAgentString(s.getUserAgentString() + " HomeflixTV");

        web.setBackgroundColor(Color.BLACK);
        web.setKeepScreenOn(true);
        web.setFocusable(true);
        web.setFocusableInTouchMode(true);
        web.requestFocus();

        web.setWebViewClient(new WebViewClient() {
            @Override
            public void onPageFinished(WebView view, String url) {
                // Homeflix menü ve oynatıcıyı açarken geçmişe kayıt ekler (history.pushState) ve WebView bunu da
                // sayfa yüklendi diye bildirir; bu yüzden burada geçmiş silinmemeli, yoksa X / geri oku çalışmaz.
                if (loadFailed) return;
                hideOffline();
                view.evaluateJavascript(navJs, null);  // tv-nav.js kendini bir kez kurar
            }

            @Override
            public void onReceivedError(WebView view, WebResourceRequest request, WebResourceError error) {
                if (request.isForMainFrame()) {
                    loadFailed = true;
                    showOffline();
                }
            }
        });

        chrome = new WebChromeClient() {
            @Override
            public void onShowCustomView(View view, CustomViewCallback callback) {
                if (customView != null) {
                    callback.onCustomViewHidden();
                    return;
                }
                customView = view;
                customCallback = callback;
                web.setVisibility(View.GONE);
                root.addView(view, new FrameLayout.LayoutParams(
                        FrameLayout.LayoutParams.MATCH_PARENT,
                        FrameLayout.LayoutParams.MATCH_PARENT));
            }

            @Override
            public void onHideCustomView() {
                if (customView == null) return;
                root.removeView(customView);
                customView = null;
                web.setVisibility(View.VISIBLE);
                web.requestFocus();
                if (customCallback != null) {
                    customCallback.onCustomViewHidden();
                    customCallback = null;
                }
            }

            @Override
            public Bitmap getDefaultVideoPoster() {
                return Bitmap.createBitmap(1, 1, Bitmap.Config.ARGB_8888);
            }
        };
        web.setWebChromeClient(chrome);
    }

    // ---- Sunucu adresi ----

    private SharedPreferences prefs() {
        return getSharedPreferences(PREFS, MODE_PRIVATE);
    }

    private boolean hasSavedUrl() {
        return prefs().contains(KEY_URL);
    }

    private String currentUrl() {
        return prefs().getString(KEY_URL, BuildConfig.DEFAULT_URL);
    }

    private void load(String url) {
        handler.removeCallbacks(retry);
        loadFailed = false;
        web.loadUrl(url);
    }

    // Bilgisayar uykuda ya da sunucu yeniden başlıyor olabilir: adresi yeniden sormak yerine kayıtlı adresi
    // sessizce tekrar dener. Mesaj WebView'in üstünde ayrı bir katmanda durur, tarayıcı geçmişine girmez.
    // Bu ekranda OK / MENU tuşu ya da ekrana dokunmak adres penceresini açar.
    private void showOffline() {
        offline = true;
        String host = Uri.parse(currentUrl()).getAuthority();
        offlineView.setText("HOMEFLIX\n\n" + host + " adresine bağlanılamıyor.\n"
                + "Bilgisayar açık mı? 5 saniye içinde tekrar denenecek.\n\n"
                + "Adresi değiştirmek için OK tuşuna basın ya da ekrana dokunun.");
        offlineView.setVisibility(View.VISIBLE);
        handler.removeCallbacks(retry);
        handler.postDelayed(retry, RETRY_MS);
        // Modem bilgisayara yeni bir adres vermiş olabilir: ağda tek bir Homeflix varsa ona geçer.
        discover(servers -> {
            if (!offline || servers.size() != 1) return;
            String url = servers.get(0)[0];
            if (!url.equals(currentUrl())) connect(url);
        });
    }

    // ---- Sunucuyu ağda bulma ----

    private interface Found {
        void done(List<String[]> servers);  // her biri {adres, bilgisayar adı}
    }

    private void findOnFirstLaunch() {
        offline = true;
        offlineView.setText("HOMEFLIX\n\nHomeflix sunucusu ağda aranıyor…");
        offlineView.setVisibility(View.VISIBLE);
        discover(servers -> {
            if (servers.size() == 1) connect(servers.get(0)[0]);
            else if (servers.size() > 1) chooseServer(servers);
            else showAddressDialog("Homeflix ağda bulunamadı. Bilgisayar açık ve aynı ağda mı? "
                    + "Bilgisayarın adresini girin (Homeflix'te Ayarlar > Diğer cihazlar'da yazar).");
        });
    }

    private void connect(String url) {
        prefs().edit().putString(KEY_URL, url).apply();
        load(url);
    }

    private void chooseServer(List<String[]> servers) {
        if (dialog != null && dialog.isShowing()) return;
        String[] labels = new String[servers.size()];
        for (int i = 0; i < labels.length; i++) {
            labels[i] = servers.get(i)[1] + "  (" + Uri.parse(servers.get(i)[0]).getAuthority() + ")";
        }
        handler.removeCallbacks(retry);
        dialog = new AlertDialog.Builder(this)
                .setTitle("Homeflix sunucusunu seçin")
                .setItems(labels, (d, i) -> connect(servers.get(i)[0]))
                .setOnCancelListener(d -> load(currentUrl()))
                .show();
    }

    // Ağa yayın yapıp ~2 saniye cevap bekler. Adres cevabı gönderenden alınır; böylece modem bilgisayara
    // yeni bir IP verse de sunucu bulunur.
    private void discover(Found cb) {
        if (discovering) return;
        discovering = true;
        new Thread(() -> {
            List<String[]> found = new ArrayList<>();
            Set<String> seen = new LinkedHashSet<>();
            try (DatagramSocket sock = new DatagramSocket()) {
                sock.setBroadcast(true);
                sock.setSoTimeout(400);
                byte[] q = DISCOVER_QUERY.getBytes(StandardCharsets.UTF_8);
                Set<InetAddress> targets = broadcastAddresses();
                long end = System.currentTimeMillis() + 2000;
                int sent = 0;
                while (System.currentTimeMillis() < end) {
                    if (sent++ < 3) {
                        for (InetAddress a : targets) {
                            try {
                                sock.send(new DatagramPacket(q, q.length, a, DISCOVERY_PORT));
                            } catch (Exception ignored) {
                            }
                        }
                    }
                    byte[] buf = new byte[512];
                    DatagramPacket p = new DatagramPacket(buf, buf.length);
                    try {
                        sock.receive(p);
                    } catch (SocketTimeoutException e) {
                        continue;
                    }
                    try {
                        JSONObject o = new JSONObject(new String(p.getData(), 0, p.getLength(), StandardCharsets.UTF_8));
                        if (!"homeflix".equals(o.optString("app"))) continue;
                        String url = "http://" + p.getAddress().getHostAddress() + ":" + o.optInt("port", 5000);
                        if (seen.add(url)) found.add(new String[]{url, o.optString("name", url)});
                    } catch (Exception ignored) {
                    }
                }
            } catch (Exception ignored) {
            }
            handler.post(() -> {
                discovering = false;
                cb.done(found);
            });
        }).start();
    }

    private static Set<InetAddress> broadcastAddresses() {
        Set<InetAddress> out = new LinkedHashSet<>();
        try {
            out.add(InetAddress.getByName("255.255.255.255"));
            for (NetworkInterface ni : Collections.list(NetworkInterface.getNetworkInterfaces())) {
                if (!ni.isUp() || ni.isLoopback()) continue;
                for (InterfaceAddress ia : ni.getInterfaceAddresses()) {
                    if (ia.getBroadcast() != null) out.add(ia.getBroadcast());
                }
            }
        } catch (Exception ignored) {
        }
        return out;
    }

    private void hideOffline() {
        if (!offline) return;
        offline = false;
        offlineView.setVisibility(View.GONE);
        web.requestFocus();
    }

    private String normalizeUrl(String raw) {
        String u = raw.trim();
        if (u.isEmpty()) return currentUrl();
        if (!u.contains("://")) u = "http://" + u;
        Uri uri = Uri.parse(u);
        if ("http".equals(uri.getScheme()) && uri.getPort() == -1 && uri.getHost() != null) {
            u = "http://" + uri.getHost() + ":5000" + (uri.getPath() == null ? "" : uri.getPath());
        }
        return u;
    }

    private void showAddressDialog(String message) {
        if (dialog != null && dialog.isShowing()) return;
        final EditText input = new EditText(this);
        input.setSingleLine(true);
        input.setInputType(InputType.TYPE_CLASS_TEXT | InputType.TYPE_TEXT_VARIATION_URI);
        input.setText(currentUrl().replaceFirst("^http://", ""));
        input.setSelectAllOnFocus(true);
        handler.removeCallbacks(retry);

        dialog = new AlertDialog.Builder(this)
                .setTitle("Homeflix sunucu adresi")
                .setMessage(message)
                .setView(input)
                .setPositiveButton("Bağlan", (d, w) -> {
                    String u = normalizeUrl(input.getText().toString());
                    prefs().edit().putString(KEY_URL, u).apply();
                    load(u);
                })
                .setNeutralButton("Ağda ara", (d, w) -> discover(servers -> {
                    if (servers.size() == 1) connect(servers.get(0)[0]);
                    else if (servers.size() > 1) chooseServer(servers);
                    else {
                        Toast.makeText(this, "Ağda Homeflix bulunamadı", Toast.LENGTH_LONG).show();
                        showAddressDialog(ADDRESS_HINT);
                    }
                }))
                .setNegativeButton("İptal", (d, w) -> load(currentUrl()))
                .setOnCancelListener(d -> load(currentUrl()))
                .show();
    }

    // ---- Tuşlar ----

    private void media(String action) {
        web.evaluateJavascript("window.hfTvMedia && window.hfTvMedia('" + action + "')", null);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        switch (keyCode) {
            case KeyEvent.KEYCODE_MENU:
                showAddressDialog(ADDRESS_HINT);
                return true;
            case KeyEvent.KEYCODE_DPAD_CENTER:
            case KeyEvent.KEYCODE_ENTER:
                if (offline) {
                    showAddressDialog(ADDRESS_HINT);
                    return true;
                }
                break;
            case KeyEvent.KEYCODE_MEDIA_PLAY_PAUSE:
                media("toggle");
                return true;
            case KeyEvent.KEYCODE_MEDIA_PLAY:
                media("play");
                return true;
            case KeyEvent.KEYCODE_MEDIA_PAUSE:
                media("pause");
                return true;
            case KeyEvent.KEYCODE_MEDIA_REWIND:
                media("back");
                return true;
            case KeyEvent.KEYCODE_MEDIA_FAST_FORWARD:
                media("fwd");
                return true;
            default:
                break;
        }

        // Tam ekran videoda sayfaya tuş gitmeyebilir; burada doğrudan yönet.
        if (customView != null && event.getRepeatCount() == 0) {
            switch (keyCode) {
                case KeyEvent.KEYCODE_DPAD_CENTER:
                case KeyEvent.KEYCODE_ENTER:
                    media("toggle");
                    return true;
                case KeyEvent.KEYCODE_DPAD_LEFT:
                    media("back");
                    return true;
                case KeyEvent.KEYCODE_DPAD_RIGHT:
                    media("fwd");
                    return true;
                case KeyEvent.KEYCODE_DPAD_UP:
                case KeyEvent.KEYCODE_DPAD_DOWN:
                    return true;
                default:
                    break;
            }
        }
        return super.onKeyDown(keyCode, event);
    }

    @Override
    public void onBackPressed() {
        if (offline) {
            super.onBackPressed();
        } else if (customView != null) {
            chrome.onHideCustomView();
        } else if (web.canGoBack()) {
            web.goBack();
        } else {
            super.onBackPressed();
        }
    }

    @Override
    protected void onPause() {
        super.onPause();
        web.onPause();
    }

    @Override
    protected void onResume() {
        super.onResume();
        web.onResume();
    }

    @Override
    protected void onDestroy() {
        handler.removeCallbacks(retry);
        root.removeAllViews();
        web.destroy();
        super.onDestroy();
    }

    private String readAsset(String name) {
        try (InputStream in = getAssets().open(name)) {
            ByteArrayOutputStream out = new ByteArrayOutputStream();
            byte[] buf = new byte[4096];
            int n;
            while ((n = in.read(buf)) > 0) out.write(buf, 0, n);
            return new String(out.toByteArray(), StandardCharsets.UTF_8);
        } catch (Exception e) {
            return "";
        }
    }
}
