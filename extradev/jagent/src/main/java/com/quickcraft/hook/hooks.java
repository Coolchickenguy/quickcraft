package com.quickcraft.hook;

import java.util.Map;
import java.util.HashMap;
import java.util.Set;
import java.util.HashSet;


public class hooks {
    private static Map<String,Set<Runnable>> listeners = new HashMap<>();
    public static void addListener(String eventName,Runnable callback) {
        if (hooks.listeners.containsKey(eventName)){
            hooks.listeners.get(eventName).add(callback);
        }else{
            HashSet<Runnable> hs = new HashSet<>();
            hs.add(callback);
            hooks.listeners.put(eventName,hs);
        }
    }
    public static void onWindowCreated() {
        // System.out.println("[Agent] Minecraft window was created!");
        if (hooks.listeners.containsKey("onWindowCreated")){
            for (Runnable listener : hooks.listeners.get("onWindowCreated")){
                Thread t = new Thread(listener);
                t.start();
            }
        }
    }
}
