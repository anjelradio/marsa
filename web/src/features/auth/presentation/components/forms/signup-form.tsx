"use client";

import { useRef } from "react";
import { cn } from "@/lib/utils";
import { FieldGroup } from "@/components/ui/field";
import TextFormField from "@/features/shared/presentation/components/forms/text-form-field";
import { appToast } from "@/features/shared/presentation/components/notifications/toast";
import SubmitButton from "@/features/shared/presentation/components/custom-buttons/submit-button";

export function SignupForm({
  className,
  ...props
}: React.ComponentProps<"div">) {
  const formRef = useRef<HTMLFormElement>(null);

  const handleSubmit = async () => {
    appToast.error("Autenticación no disponible", "Aún no hay un proveedor de autenticación configurado.");
  };

  return (
    <div className={cn("flex flex-col gap-6", className)} {...props}>
      <form ref={formRef} action={handleSubmit}>
        <FieldGroup>
          <TextFormField
            id="name"
            name="name"
            label="Nombre"
            placeholder="Tu nombre"
            type="text"
            autoComplete="name"
          />
          <TextFormField
            id="email"
            name="email"
            label="Email"
            placeholder="tu@correo.com"
            type="email"
            autoComplete="email"
          />
          <TextFormField
            id="password"
            name="password"
            label="Contraseña"
            placeholder="Mínimo 8 caracteres"
            type="password"
            autoComplete="new-password"
          />
          <SubmitButton text="Registrarse" pendingText="Registrando..." />
        </FieldGroup>
      </form>
    </div>
  );
}
