package com.quickcraft.agent;

import java.lang.instrument.*;

public class WindowHookAgent {
    public static void premain(String agentArgs, Instrumentation inst) {
        inst.addTransformer(new transformer());
    }
}
