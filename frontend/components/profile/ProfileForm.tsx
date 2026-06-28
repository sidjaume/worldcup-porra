"use client";

import { useActionState } from "react";
import { Save } from "lucide-react";
import { updateProfileAction } from "@/app/actions";
import { Button } from "@/components/ui/Button";
import { Field, FormMessage, TextInput } from "@/components/ui/Field";
import type { User } from "@/types/api";

export function ProfileForm({ user }: { user: User }) {
  const [state, action, pending] = useActionState(updateProfileAction, {});

  return (
    <form action={action} className="grid gap-4">
      <Field label="Display name">
        <TextInput defaultValue={user.display_name} name="display_name" required />
      </Field>
      <Field label="Email">
        <TextInput disabled value={user.email} />
      </Field>
      <FormMessage message={state.error} />
      {state.ok ? <p className="text-sm font-medium text-grass">Profile saved.</p> : null}
      <Button disabled={pending} type="submit">
        <Save aria-hidden="true" size={16} />
        Save profile
      </Button>
    </form>
  );
}
