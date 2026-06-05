package org.telegram.ui;

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
import org.telegram.messenger.NotificationCenter;
import org.telegram.messenger.R;
import org.telegram.messenger.UserConfig;
import org.telegram.ui.ActionBar.ActionBar;
import org.telegram.ui.ActionBar.BaseFragment;
import org.telegram.ui.ActionBar.Theme;

public class WeryGramPremiumActivity extends BaseFragment {

    private static final String KEY_VISUAL_PREMIUM = "visual_premium";
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
            
            // 🔴 ВАЖНО! Обновляем UI когда включаем/выключаем премиум
            if (key.equals(KEY_VISUAL_PREMIUM)) {
                // Уведомляем что изменился статус премиума
                NotificationCenter.getInstance(currentAccount).postNotificationName(NotificationCenter.currentUserPremiumStatusChanged);
                NotificationCenter.getGlobalInstance().postNotificationName(NotificationCenter.premiumStatusChangedGlobal);
                
                // Обновляем MessagesController
                MessagesController controller = MessagesController.getInstance(currentAccount);
                controller.updatePremium(checked);
                
                // Обновляем текущего пользователя - ТОЛЬКО premium, БЕЗ verified
                org.telegram.tgnet.TLRPC.User user = UserConfig.getInstance(currentAccount).getCurrentUser();
                if (user != null) {
                    user.premium = checked;
                    // НЕ устанавливаем verified - только premium!
                }
            }
            
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
