"use client";

import { useActionState, useId } from "react";
import { Save } from "lucide-react";
import { updateProfileAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, FormSuccess, TextInput } from "@/components/ui/Field";
import type { User } from "@/types/api";

export function ProfileForm({ user }: { user: User }) {
  const [state, action, pending] = useActionState(updateProfileAction, {});
  const feedbackId = useId();
  const describedBy = state.error || state.ok ? feedbackId : undefined;

  return (
    <form action={action} aria-describedby={describedBy} className="grid gap-4">
      <Field label="Display name">
        <TextInput
          aria-describedby={describedBy}
          aria-invalid={state.error ? true : undefined}
          defaultValue={user.display_name}
          name="display_name"
          required
        />
      </Field>
      <Field label="Email">
        <TextInput disabled value={user.email} />
      </Field>
      <FormMessage id={state.error ? feedbackId : undefined} message={state.error} />
      <FormSuccess id={state.ok ? feedbackId : undefined} message={state.ok ? "Profile saved." : undefined} />
      <Button disabled={pending} type="submit">
        <Save aria-hidden="true" size={16} />
        {pending ? "Saving" : "Save profile"}
      </Button>
    </form>
  );
}
