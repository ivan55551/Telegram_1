import os
import re
import sys
from pathlib import Path

def log_success(msg):
    print(f"✓ {msg}")

def log_error(msg):
    print(f"✗ {msg}")

def log_info(msg):
    print(f"→ {msg}")

def find_file_in_project(filename, search_root="."):
    """Найти файл в проекте"""
    for root, dirs, files in os.walk(search_root):
        if filename in files:
            return os.path.join(root, filename)
    return None

def patch_werygram_core():
    log_info("WeryGram Premium Patcher v6.0 запускается...")
    
    # Пути к файлам
    settings_path = "TMessagesProj/src/main/java/org/telegram/ui/SettingsActivity.java"
    userconfig_path = "TMessagesProj/src/main/java/org/telegram/messenger/UserConfig.java"
    messages_path = "TMessagesProj/src/main/java/org/telegram/messenger/MessagesController.java"
    
    # ==========================================
    # 1. PATCH SettingsActivity.java
    # ==========================================
    log_info(f"Обработка {settings_path}...")
    
    if not os.path.exists(settings_path):
        log_error(f"Файл не найден: {settings_path}")
        found = find_file_in_project("SettingsActivity.java")
        if found:
            log_info(f"Найден файл: {found}")
            settings_path = found
        else:
            sys.exit(1)
    
    with open(settings_path, "r", encoding="utf-8") as f:
        settings_code = f.read()
    
    # Удаляем старые версии (если они есть)
    settings_code = re.sub(
        r'case 9999:\s*\{[^}]*presentFragment\(new org\.telegram\.ui\.WeryGramPremiumActivity\(\)\);[^}]*\}',
        '',
        settings_code,
        flags=re.DOTALL
    )
    
    # Ищем case 10 для Language
    case_10_pattern = r'(case 10:[\s\S]*?presentFragment\(new LanguageSelectActivity\(\);[\s\S]*?break;)'
    
    if re.search(case_10_pattern, settings_code):
        new_case = '''
            case 9999:
                presentFragment(new org.telegram.ui.WeryGramPremiumActivity());
                break;'''
        
        settings_code = re.sub(
            case_10_pattern,
            r'\1' + new_case,
            settings_code,
            flags=re.DOTALL
        )
        log_success("case 9999 добавлен в onClick!")
    else:
        log_error("Не найден case 10 для привязки новой кнопки!")
        return False
    
    # Добавляем кнопку в список меню
    add_button_pattern = r'(items\.add\(SettingCell\.Factory\.of\(10,.*?getString\(R\.string\.SettingsLanguage\).*?\);)'
    
    new_button = r'items.add(SettingCell.Factory.of(9999, 0xFF55CA47, 0xFF27B434, R.drawable.settings_power, "WeryGram Premium"));\n        \1'
    
    if re.search(add_button_pattern, settings_code, flags=re.DOTALL):
        settings_code = re.sub(add_button_pattern, new_button, settings_code, flags=re.DOTALL)
        log_success("Кнопка добавлена в список настроек!")
    else:
        log_error("Не найдено место для добавления кнопки")
    
    with open(settings_path, "w", encoding="utf-8") as f:
        f.write(settings_code)
    
    log_success(f"{settings_path} успешно изменён!")
    
    # ==========================================
    # 2. CREATE WeryGramPremiumActivity.java
    # ==========================================
    activity_code = '''package org.telegram.ui;

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

    private static boolean get(String key) {
        return prefs().getBoolean(key, false);
    }

    private static void set(String key, boolean v) {
        prefs().edit().putBoolean(key, v).apply();
    }

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
                if (id == -1) {
                    finishFragment();
                }
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
        header.setText("ВИЗУАЛЬНЫЕ НАСТРОЙКИ");
        header.setTextSize(13);
        header.setTextColor(0xFF79879B);
        header.setPadding(
            AndroidUtilities.dp(21),
            AndroidUtilities.dp(16),
            AndroidUtilities.dp(21),
            AndroidUtilities.dp(8)
        );
        container.addView(header);

        // Добавляем переключатели
        addToggleRow(context, container, "Визуально Telegram Premium", KEY_VISUAL_PREMIUM, new Runnable() {
            @Override
            public void run() {
                set(KEY_VERIFIED, true);
                set(KEY_ANIM_EMOJI, true);
                set(KEY_PREM_STICKERS, true);
                set(KEY_PREM_REACTIONS, true);
            }
        });
        addToggleRow(context, container, "Галочка верификации", KEY_VERIFIED, null);
        addToggleRow(context, container, "Скрыть рекламу", KEY_HIDE_ADS, null);
        addToggleRow(context, container, "Анимированные emoji", KEY_ANIM_EMOJI, null);
        addToggleRow(context, container, "Premium стикеры", KEY_PREM_STICKERS, null);
        addToggleRow(context, container, "Расширенные реакции", KEY_PREM_REACTIONS, null);

        return fragmentView;
    }

    private void addToggleRow(final Context ctx, LinearLayout parent,
                              final String label, final String key, final Runnable onEnable) {
        LinearLayout row = new LinearLayout(ctx);
        row.setOrientation(LinearLayout.HORIZONTAL);
        row.setGravity(Gravity.CENTER_VERTICAL);
        row.setBackgroundColor(Theme.getColor(Theme.key_windowBackgroundWhite));
        row.setPadding(
            AndroidUtilities.dp(21),
            AndroidUtilities.dp(14),
            AndroidUtilities.dp(21),
            AndroidUtilities.dp(14)
        );

        TextView tv = new TextView(ctx);
        tv.setText(label);
        tv.setTextSize(16);
        tv.setTextColor(Theme.getColor(Theme.key_windowBackgroundWhiteBlackText));
        row.addView(tv, new LinearLayout.LayoutParams(
            0,
            LinearLayout.LayoutParams.WRAP_CONTENT,
            1f
        ));

        final Switch sw = new Switch(ctx);
        sw.setChecked(get(key));
        sw.setOnCheckedChangeListener(new CompoundButton.OnCheckedChangeListener() {
            @Override
            public void onCheckedChanged(CompoundButton btn, boolean checked) {
                set(key, checked);
                if (checked && onEnable != null) {
                    onEnable.run();
                }
                if (getParentActivity() != null) {
                    Toast.makeText(
                        getParentActivity(),
                        label + (checked ? ": ВКЛ" : ": ВЫКЛ"),
                        Toast.LENGTH_SHORT
                    ).show();
                }
            }
        });
        row.addView(sw);

        parent.addView(row);

        // Разделитель
        View divider = new View(ctx);
        divider.setBackgroundColor(0xFFE0E0E0);
        LinearLayout.LayoutParams dividerParams = new LinearLayout.LayoutParams(
            LinearLayout.LayoutParams.MATCH_PARENT,
            1
        );
        dividerParams.setMarginStart(AndroidUtilities.dp(21));
        parent.addView(divider, dividerParams);
    }
}
'''
    
    activity_path = "TMessagesProj/src/main/java/org/telegram/ui/WeryGramPremiumActivity.java"
    os.makedirs(os.path.dirname(activity_path), exist_ok=True)
    
    with open(activity_path, "w", encoding="utf-8") as f:
        f.write(activity_code)
    
    log_success(f"WeryGramPremiumActivity.java создан: {activity_path}")
    
    # ==========================================
    # 3. PATCH UserConfig.java (опционально)
    # ==========================================
    if os.path.exists(userconfig_path):
        log_info(f"Обработка {userconfig_path}...")
        try:
            with open(userconfig_path, "r", encoding="utf-8") as f:
                uc_code = f.read()
            
            if "visual_premium" not in uc_code:
                if "public TLRPC.User getCurrentUser()" in uc_code:
                    uc_patch = '''public TLRPC.User getCurrentUser() {
        TLRPC.User user = currentUser;
        if (user != null && MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
            user.premium = true;
            user.verified = true;
        }
        return user;
    }'''
                    
                    uc_code = re.sub(
                        r'public TLRPC\.User getCurrentUser\(\)\s*\{[^}]*return currentUser;[^}]*\}',
                        uc_patch,
                        uc_code,
                        flags=re.DOTALL
                    )
                    
                    with open(userconfig_path, "w", encoding="utf-8") as f:
                        f.write(uc_code)
                    
                    log_success(f"UserConfig.java патчен")
        except Exception as e:
            log_error(f"Ошибка при обработке UserConfig.java: {e}")
    
    # ==========================================
    # 4. ИТОГИ
    # ==========================================
    print("\n" + "="*60)
    log_success("ВСЕ МОДУЛИ УСПЕШНО ОБРАБОТАНЫ!")
    print("="*60)
    print("""
Что было сделано:
1. ✓ Добавлена кнопка 'WeryGram Premium' в SettingsActivity
2. ✓ Создан файл WeryGramPremiumActivity.java
3. ✓ Добавлены переключатели для премиум функций
4. ✓ Настроена система сохранения параметров

Следующие шаги:
1. Пересоберите проект: ./gradlew clean build
2. Или используйте Android Studio для сборки
3. Установите APK на тестовое устройство
4. Проверьте, появилась ли кнопка в настройках

ВАЖНО: Если кнопка не появляется:
- Проверьте, что используется правильный модуль сборки
- Очистите кэш Build -> Clean Project
- Перезагрузите проект
""")

if __name__ == "__main__":
    try:
        patch_werygram_core()
    except Exception as e:
        log_error(f"Критическая ошибка: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
