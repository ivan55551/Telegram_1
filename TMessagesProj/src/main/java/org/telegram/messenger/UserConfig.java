    public TLRPC.User getCurrentUser() {
        synchronized (sync) {
            if (currentUser != null && MessagesController.getGlobalMainSettings().getBoolean("visual_premium", false)) {
                currentUser.premium = true;
                // НЕ устанавливаем verified - только premium!
            }
            return currentUser;
        }
    }
