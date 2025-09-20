package com.quickcraft.agent;

import java.lang.instrument.*;

import org.json.JSONObject;

public class WindowHookAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        String configString = System.getProperty("com.quickcraft.config");
        JSONObject config = new JSONObject(configString);
        inst.addTransformer(new transformer(config));
    }
}
