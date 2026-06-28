import { redirect } from "next/navigation";
import { ApiError } from "@/lib/api/client";
import { getCurrentUser } from "@/lib/api/users";
import { getSession } from "@/lib/auth/session";

export async function requireSession() {
  const session = await getSession();
  if (!session) {
    redirect("/");
  }

  try {
    const user = await getCurrentUser(session.accessToken);
    return { ...session, user };
  } catch (error) {
    if (error instanceof ApiError && error.status === 401) {
      redirect("/auth/refresh");
    }
    throw error;
  }
}
