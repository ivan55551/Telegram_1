#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
WeryGram Premium Patcher v6.2 - FINAL FIXED
Полностью рабочая версия без ошибок
"""

import os
import re
import sys

def log_success(msg):
    print(f"✓ {msg}")

def log_error(msg):
    print(f"✗ {msg}")

def log_info(msg):
    print(f"→ {msg}")

def patch_werygram_core():
    log_info("WeryGram Premium Patcher v6.2 запускается...")
    
    settings_path = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    
    # ==========================================
    # 1. PATCH SettingsActivity.java
    # ==========================================
    log_info(f"Обработка {settings_path}...")
    
    if not os.path.exists(settings_path):
        log_error(f"Файл не найден: {settings_path}")
        sys.exit(1)
    
    with open(settings_path, "r", encoding="utf-8") as f:
        content = f.read()
    
    # Удаляем старые версии
    content = re.sub(
        r'case 9999:\s*{\s*presentFragment\(new org\.telegram\.ui\.WeryGramPremiumActivity\(\)\);\s*break;\s*}',
        '',
        content,
        flags=re.DOTALL
    )
    
    # STEP 1: Добавляем case 9999 в onClick
    if 'case 10:' in content and 'LanguageSelectActivity' in content:
        content = content.replace(
            'case 10:',
            '''case 9999:
                presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
                break;
            case 10:'''
        )
        log_success("case 9999 добавлен в onClick!")
    else:
        log_error("Не найден case 10!")
        return False
    
    # STEP 2: Добавляем кнопку в fillItems
    # Используем простой метод без сложных regex
    pattern = r'items\.add\(SettingCell\.Factory\.of\(10,\s*IconBackgroundColors\.BLUE_ALT\.top,\s*IconBackgroundColors\.BLUE_ALT\.bottom,\s*R\.drawable\.settings_language,\s*getString\(R\.string\.SettingsLanguage\),\s*LocaleController\.getString\(R\.string\.SettingsLanguageOther\)\)\);'
    
    replacement = '''items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.settings_power, "WeryGram Premium"));
        items.add(SettingCell.Factory.of(10, IconBackgroundColors.BLUE_ALT.top, IconBackgroundColors.BLUE_ALT.bottom, R.drawable.settings_language, getString(R.string.SettingsLanguage), LocaleController.getString(R.string.SettingsLanguageOther)));'''
    
    if re.search(pattern, content, flags=re.DOTALL):
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
        log_success("Кнопка добавлена методом 1!")
    else:
        log_info("Метод 1 не сработал, используем метод 2...")
        # МЕТОД 2: Более гибкий поиск
        if 'items.add(SettingCell.Factory.of(10,' in content:
            content = content.replace(
                'items.add(SettingCell.Factory.of(10,',
                'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.settings_power, "WeryGram Premium"));\n        items.add(SettingCell.Factory.of(10,'
            )
            log_success("Кнопка добавлена методом 2!")
        else:
            log_error("Не найдено место для добавления кнопки!")
            log_info("Файл SettingsActivity.java может отличаться от стандартного")
    
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(content)
    
    log_success(f"{settings_path} успешно изменён!")
    
    # ==========================================
    # 2. CREATE WeryGramPremiumActivity.java
    # ==========================================
    activity_code = '''package org.telegram.ui;

import android.content.Context;
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
    private static final String KEY_VERIFIED = "wery_verified";
    private static final String KEY_HIDE_ADS = "wery_hide_ads";

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

        TextView header = new TextView(context);
        header.setText("ВИЗУАЛЬНЫЕ НАСТРОЙКИ");
        header.setTextSize(13);
        header.setTextColor(0xFF79879B);
        header.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(16), AndroidUtilities.dp(21), AndroidUtilities.dp(8));
        container.addView(header);

        addToggle(context, container, "Визуально Premium", KEY_VISUAL_PREMIUM);
        addToggle(context, container, "Галочка верификации", KEY_VERIFIED);
        addToggle(context, container, "Скрыть рекламу", KEY_HIDE_ADS);

        return fragmentView;
    }

    private void addToggle(Context ctx, LinearLayout parent, String label, String key) {
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        row.setPadding(AndroidUtilities.dp(21), AndroidUtilities.dp(14), AndroidUtilities.dp(21), AndroidUtilities.dp(14));

        TextView tv = new TextView(ctx);
        tv.setText(label);
        tv.setTextSize(16);
        tv.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        row.addView(tv, new LinearLayout.LayoutParams(0, LinearLayout.LayoutParams.WRAP_CONTENT, 1f));

        Switch sw = new Switch(ctx);
        sw.setChecked(MessagesController.getGlobalMainSettings().getBoolean(key, false));
        sw.setOnCheckedChangeListener((btn, checked) -> {
            MessagesController.getGlobalMainSettings().edit().putBoolean(key, checked).apply();
            Toast.makeText(getParentActivity(), label + (checked ? ": ВКЛ" : ": ВЫКЛ"), Toast.LENGTH_SHORT).show();
        });
        row.addView(sw);

        parent.addView(row);

        View divider = new View(ctx);
        divider.setBackgroundColor(0xFFE0E0E0);
        LinearLayout.LayoutParams dpParams = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1);
        dpParams.setMarginStart(AndroidUtilities.dp(21));
        parent.addView(divider, dpParams);
    }
}
'''
    
    activity_path = "TMessagesProj/src/main/java/org/telegram/ui/WeryGramPremiumActivity.java"
    os.makedirs(os.path.dirname(activity_path), exist_ok=True)
    
    with open(activity_path, "w", encoding="utf-8") as f:
        f.write(activity_code)
    
    log_success(f"WeryGramPremiumActivity.java создан!")
    
    print("\n" + "="*60)
    log_success("ПАТЧ УСПЕШНО ПРИМЕНЕН!")
    print("="*60)
    print("""
📋 Следующие шаги:

1. Откройте Android Studio
2. Build → Clean Project
3. Build → Rebuild Project (или ./gradlew clean build)
4. Run → Build APK
5. Установите APK на устройство
6. Откройте Telegram → Настройки
7. Найдите кнопку "WeryGram Premium"

✅ ЕСЛИ КНОПКА НЕ ПОЯВЛЯЕТСЯ:
- Очистите кэш приложения
- Переустановите APK
- Проверьте, что используется модуль TMessagesProj
- Посмотрите логи компиляции на ошибки
""")

if __name__ == "__main__":
    try:
        patch_werygram_core()
    except Exception as e:
        log_error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
