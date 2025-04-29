package com.quickcraft.agent;

import java.lang.instrument.*;
import java.security.ProtectionDomain;

import org.objectweb.asm.*;
import org.objectweb.asm.commons.*;
public class transformer implements ClassFileTransformer {
            @Override
        public byte[] transform(ClassLoader loader, String className, Class<?> classBeingRedefined,
                                ProtectionDomain protectionDomain, byte[] classfileBuffer) {
            // Don't event check java classes because the checker uses them
            if (className.startsWith("java")) return classfileBuffer;
            if (!className.equals(System.getProperty("hookedClass"))) return classfileBuffer;
            //return classfileBuffer;
            ClassReader reader = new ClassReader(classfileBuffer);
            ClassWriter writer = new ClassWriter(reader, ClassWriter.COMPUTE_FRAMES | ClassWriter.COMPUTE_MAXS);

            ClassVisitor visitor = new ClassVisitor(Opcodes.ASM9, writer) {
                @Override
                public MethodVisitor visitMethod(int access, String name, String descriptor,
                                                 String signature, String[] exceptions) {

                    MethodVisitor mv = super.visitMethod(access, name, descriptor, signature, exceptions);

                    if (name.equals("<init>")) {
                        // Explicitly declare AdviceAdapter first, then return it
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
