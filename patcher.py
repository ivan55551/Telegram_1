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
    log_info("WeryGram Premium Patcher v6.1 запускается...")
    
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
    
    # ИСПРАВКА 1: Правильно найти и заменить onClick switch
    # Ищем точку для добавления case 9999
    if 'case 10:' in content and 'LanguageSelectActivity' in content:
        # Вставляем ДО case 10
        content = content.replace(
            'case 10:',
            '''case 9999:
                presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
                break;
            case 10:'''
        )
        log_success("case 9999 добавлен в onClick!")
    else:
        log_error("Не найден case 10 для добавления case 9999!")
        return False
    
    # ИСПРАВКА 2: Правильно добавить кнопку в fillItems
    # Ищем items.add(SettingCell.Factory.of(10, ... SettingsLanguage
    language_button_pattern = r'items\.add\(SettingCell\.Factory\.of\(10,\s*IconBackgroundColors\.BLUE_ALT\.top,\s*IconBackgroundColors\.BLUE_ALT\.bottom,\s*R\.drawable\.settings_language,\s*getString\(R\.string\.SettingsLanguage\),\s*LocaleController\.getString\(R\.string\.SettingsLanguageOther\).*?\)\);'
    
    new_button_code = '''items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.settings_power, "WeryGram Premium"));
        items.add(SettingCell.Factory.of(10, IconBackgroundColors.BLUE_ALT.top, IconBackgroundColors.BLUE_ALT.bottom, R.drawable.settings_language, getString(R.string.SettingsLanguage), LocaleController.getString(R.string.SettingsLanguageOther)));'''
    
    if re.search(language_button_pattern, content, flags=re.DOTALL):
        content = re.sub(language_button_pattern, new_button_code, content, flags=re.DOTALL)
        log_success("Кнопка добавлена в список!")
    else:
        log_error("Не найдено место для добавления кнопки - используем альтернативный способ")
        # Альтернатива: найти просто items.add и case 10
        content = re.sub(
            r'(items\.add\(SettingCell\.Factory\.of\(10,.*?SettingsLanguage.*?\)\);)',
            r'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.settings_power, "WeryGram Premium"));\n        \1',
            content,
            flags=re.DOTALL
        )
        log_success("Кнопка добавлена (альтернативный метод)")
    
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
        LinearLayout.LayoutParams dp = new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT, 1);
        dp.setMarginStart(AndroidUtilities.dp(21));
        parent.addView(divider, dp);
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
    print("Действия:\n1. Пересоберите: ./gradlew clean build\n2. Установите APK\n3. Проверьте появление кнопки в Настройки")

if __name__ == "__main__":
    try:
        patch_werygram_core()
    except Exception as e:
        log_error(f"Ошибка: {e}")
        import traceback
        traceback.print_exc()
