package com.quickcraft.agent;

import java.lang.instrument.*;
import java.security.ProtectionDomain;

import org.objectweb.asm.*;
import org.objectweb.asm.commons.*;
import org.json.JSONObject;

public class transformer implements ClassFileTransformer {
    JSONObject config;
    transformer(JSONObject config) {
        super();
        this.config = config;
    }

    @Override
    public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
            ProtectionDomain protectionDomain, byte[] classfileBuffer) {
        // Don't check java or org.json classes because the checker uses them
        if (className.startsWith("java"))
            return classfileBuffer;
        if (className.startsWith("org.json"))
            return classfileBuffer;
        if (!className.equals(config.getString("windowClassName")))
            return classfileBuffer;
        ClassReader reader = new ClassReader(classfileBuffer);
        ClassWriter writer = new ClassWriter(reader, ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);

        ClassVisitor visitor = new ClassVisitor(Opcodes.ASM9, writer) {
            @Override
            public MethodVisitor visitMethod(int access, String name, String descriptor,
                    String signature, String[] exceptions) {

                MethodVisitor mv = super.visitMethod(access, name, descriptor, signature, exceptions);

                if (name.equals("<init>")) {
                    // System.out.println("[Agent] Remapping init method");
                    return new AdviceAdapter(Opcodes.ASM9, mv, access, name, descriptor) {
                        @Override
                        protected void onMethodExit(int opcode) {
                            if (opcode == RETURN) {
                                visitMethodInsn(INVOKESTATIC,
                                        "com/quickcraft/hook/hooks", "onWindowCreated", "()V", false);
                            }
                        }
                    };
                }

                return mv;
            }
        };

        reader.accept(visitor, ClassReader.EXPAND_FRAMES);
        return writer.toByteArray();
    }
}
