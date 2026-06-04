import os
import re
import sys

def patch_werygram_core():
    settings_path = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    userconfig_path = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
    messages_path = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    ui_dir = "TMessagesProj/src/main/java/org/telegram/ui"

    if not os.path.exists(settings_path):
        print(f"KRITICHESKAYA OSHIBKA: Fajl ne najden: {settings_path}")
        sys.exit(1)

    print("WeryGram Premium Patcher v5.0 zapuskaetsya...")

    # ==========================================
    # 1. SettingsActivity — кнопка + переход на экран
    # ==========================================
    with open(settings_path, "r", encoding="utf-8") as f:
        code = f.read()

    # Чистим старые версии
    code = re.sub(r'case 9999:.*?break;', '', code, flags=re.DOTALL)
    code = re.sub(r'items\.add\(SettingCell\.Factory\.of\(9999,[\s\S]*?\);\s*', '', code)
    code = re.sub(r'items\.add\(UItem\.asCheck\(9999,[\s\S]*?\);\s*', '', code)

    # Кнопка WeryGram Premium
    werygram_btn = 'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.msg_settings, "WeryGram Premium"));'

    match_notif = re.search(r'(items\.add\([\s\S]*?[nN]otif[\s\S]*?\);)', code)
    if match_notif:
        anchor = match_notif.group(1)
        code = code.replace(anchor, f'{werygram_btn}\n        {anchor}', 1)
        print("OK Knopka WeryGram dobavlena v verx spiska nastroek!")
    else:
        code = code.replace("switch (item.id) {", f"{werygram_btn}\n        switch (item.id) {{", 1)
        print("OK Knopka dobavlena rezervnym metodom.")

    # Обработчик клика — открываем новый экран
    switch_anchor = "switch (item.id) {"
    if switch_anchor in code:
        click_logic = """\
case 9999: {
            presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
            break;
        }"""
        code = code.replace(switch_anchor, f"{switch_anchor}\n            {click_logic}", 1)
        print("OK Obrabotchik klika dobavlen — otkryvaet novyj ekran!")

    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(code)

    # ==========================================
    # 2. UserConfig — включаем premium
    # ==========================================
    if os.path.exists(userconfig_path):
        with open(userconfig_path, "r", encoding="utf-8") as f:
            uc_code = f.read()

        if "visual_premium" not in uc_code:
            uc_anchor = "public TLRPC.User getCurrentUser() {"
            if uc_anchor in uc_code:
                uc_injection = """public TLRPC.User getCurrentUser() {
        if (currentUser != null && org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
            currentUser.premium = true;
            currentUser.verified = true;
        }"""
                uc_code = uc_code.replace(uc_anchor, uc_injection, 1)
                with open(userconfig_path, "w", encoding="utf-8") as f:
                    f.write(uc_code)
                print("OK UserConfig: premium=true vnedren!")

    # ==========================================
    # 3. MessagesController — перехват getUser()
    # ==========================================
    if os.path.exists(messages_path):
        with open(messages_path, "r", encoding="utf-8") as f:
            mc_code = f.read()

        if "visual_premium" not in mc_code:
            # Точная сигнатура из реального файла
            OLD = (
                "public TLRPC.User getUser(Long id) {\n"
                "        if (id == 0) {\n"
                "            return UserConfig.getInstance(currentAccount).getCurrentUser();\n"
                "        }\n"
                "        return users.get(id);\n"
                "    }"
            )
            NEW = """\
public TLRPC.User getUser(Long id) {
        if (id == 0) {
            return UserConfig.getInstance(currentAccount).getCurrentUser();
        }
        TLRPC.User user = users.get(id);
        if (user != null && id != null && id.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                user.premium = true;
                user.verified = true;
            }
        }
        return user;
    }"""
            if OLD in mc_code:
                mc_code = mc_code.replace(OLD, NEW, 1)
                print("OK MessagesController: perekhvatchik getUser() dobavlen!")
            else:
                mc_code = re.sub(
                    r'public TLRPC\.User getUser\((Long|Integer)\s+(\w+)\)\s*\{\s*return\s+(\w+)\.get\(\2\);\s*\}',
                    r'''public TLRPC.User getUser(\1 \2) {
        TLRPC.User user = \3.get(\2);
        if (user != null && \2 != null && \2.equals(UserConfig.getInstance(currentAccount).getClientUserId())) {
            if (org.telegram.messenger.MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                user.premium = true;
                user.verified = true;
            }
        }
        return user;
    }''',
                    mc_code
                )
                print("OK MessagesController: perekhvatchik dobavlen (regex).")

            with open(messages_path, "w", encoding="utf-8") as f:
                f.write(mc_code)

    # ==========================================
    # 4. Создаём WeryGramPremiumActivity.java
    #    Только стандартные Android классы — никаких RecyclerView
    # ==========================================
    activity_code = """\
package org.telegram.ui;

import android.content.Context;
import android.content.SharedPreferences;
import android.view.Gravity;
import android.view.View;
import android.widget.CompoundButton;
import android.widget.FrameLayout;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import org.telegram.messenger.AndroidUtilities;
import org.telegram.messenger.MessagesController;
import org.telegram.messenger.R;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;

public class WeryGramPremiumActivity extends BaseFragment {

    private static final String KEY_VISUAL_PREMIUM = "visual_premium";
    private static final String KEY_VERIFIED       = "wery_verified";
    private static final String KEY_HIDE_ADS       = "wery_hide_ads";
    private static final String KEY_ANIM_EMOJI     = "wery_anim_emoji";
    private static final String KEY_PREM_STICKERS  = "wery_prem_stickers";
    private static final String KEY_PREM_REACTIONS = "wery_prem_reactions";

    private static SharedPreferences prefs() {
        return MessagesController.getGlobalMainSettings();
    }
    private static boolean get(String key) { return prefs().getBoolean(key, false); }
    private static void set(String key, boolean v) { prefs().edit().putBoolean(key, v).apply(); }

    @Override
    public boolean onFragmentCreate() {
        super.onFragmentCreate();
        return true;
    }

    @Override
    public View createView(Context context) {
        actionBar.setBackButtonImage(R.drawable.ic_ab_back);
        actionBar.setTitle("WeryGram Premium");
        actionBar.setAllowOverlayTitle(true);
        actionBar.setActionBarMenuOnItemClick(new ActionBar.ActionBarMenuOnItemClick() {
            @Override
            public void onItemClick(int id) {
                if (id == -1) finishFragment();
            }
        });

        FrameLayout root = new FrameLayout(context);
        root.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundGray));
        fragmentView = root;

        ScrollView scroll = new ScrollView(context);
        root.addView(scroll, new FrameLayout.LayoutParams(
            FrameLayout.LayoutParams.MATCH_PARENT,
            FrameLayout.LayoutParams.MATCH_PARENT));

        LinearLayout container = new LinearLayout(context);
        container.setOrientation(LinearLayout.VERTICAL);
        scroll.addView(container);

        // Заголовок
        TextView header = new TextView(context);
        header.setText("VIZUALNYE NASTROYKI");
        header.setTextSize(13);
        header.setTextColor(0xFF79879B);
        header.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(16),
            AndroidUtilities.dp(21), AndroidUtilities.dp(8));
        container.addView(header);

        // Тоглы
        addRow(context, container, "Vizualno Telegram Premium", KEY_VISUAL_PREMIUM, new Runnable() {
            @Override public void run() {
                set(KEY_VERIFIED, true);
                set(KEY_ANIM_EMOJI, true);
                set(KEY_PREM_STICKERS, true);
                set(KEY_PREM_REACTIONS, true);
            }
        });
        addRow(context, container, "Galocka verifikacii",   KEY_VERIFIED,       null);
        addRow(context, container, "Skryt reklamu",         KEY_HIDE_ADS,       null);
        addRow(context, container, "Animirovannye emoji",   KEY_ANIM_EMOJI,     null);
        addRow(context, container, "Premium stikery",       KEY_PREM_STICKERS,  null);
        addRow(context, container, "Rasshirennye reakcii",  KEY_PREM_REACTIONS, null);

        return fragmentView;
    }

    private void addRow(final Context ctx, LinearLayout parent,
                        final String label, final String key, final Runnable onEnable) {
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        row.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(14),
            AndroidUtilities.dp(21), AndroidUtilities.dp(14));

        TextView tv = new TextView(ctx);
        tv.setText(label);
        tv.setTextSize(16);
        tv.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        row.addView(tv, new LinearLayout.LayoutParams(0,
            LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        final Switch sw = new Switch(ctx);
        sw.setChecked(get(key));
        sw.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton btn, boolean checked) {
                set(key, checked);
                if (checked && onEnable != null) onEnable.run();
                if (getParentActivity() != null)
                    Toast.makeText(getParentActivity(),
                        label + (checked ? ": ON" : ": OFF"),
                        Toast.LENGTH_SHORT).show();
            }
        });
        row.addView(sw);

        parent.addView(row);

        View divider = new View(ctx);
        divider.setBackgroundColor(0xFFE0E0E0);
        LinearLayout.LayoutParams dp = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT, 1);
        dp.setMarginStart(AndroidUtilities.dp(21));
        parent.addView(divider, dp);
    }
}
"""

    # Записываем во все модули
    MODULE_DIRS = [
        "TMessagesProj/src/main/java/org/telegram/ui",
        "TMessagesProj_App/src/main/java/org/telegram/ui",
        "TMessagesProj_AppHockeyApp/src/main/java/org/telegram/ui",
        "TMessagesProj_AppHuawei/src/main/java/org/telegram/ui",
        "TMessagesProj_AppStandalone/src/main/java/org/telegram/ui",
    ]
    found = set(MODULE_DIRS)
    for root, dirs, _ in os.walk("."):
        norm = root.replace(os.sep, "/").lstrip("./")
        if norm.endswith("org/telegram/ui") and "/src/main/java/" in norm:
            found.add(norm)

    for d in sorted(found):
        os.makedirs(d, exist_ok=True)
        out = os.path.join(d, "WeryGramPremiumActivity.java")
        with open(out, "w", encoding="utf-8") as f:
            f.write(activity_code)
        print(f"OK WeryGramPremiumActivity.java -> {out}")

    print("\nVSE MODULI USPESHNO MODIFICIROVANY! Zapuskajte sborku.")

if __name__ == "__main__":
    patch_werygram_core()
    
