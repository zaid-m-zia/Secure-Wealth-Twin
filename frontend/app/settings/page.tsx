"use client";

import { FormEvent, useEffect, useState } from "react";
import { Bell, Eye, KeyRound, Link2, LockKeyhole, Monitor, ShieldCheck, TriangleAlert, UserRound } from "lucide-react";
import { useRouter } from "next/navigation";
import { ErrorState, LoadingState } from "@/components/data-state";
import { SecurePage } from "@/components/secure-page";
import { ThemeToggle } from "@/components/theme-toggle";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { apiClient } from "@/services/api";
import { fetchProfile, logoutUser } from "@/services/auth";
import { CurrentUser, UserProfile } from "@/types/auth";
import { getStoredProfile } from "@/utils/storage";

const unavailable = ["Password changes", "Notification preferences", "Privacy controls", "Connected accounts", "Data export"];
const unavailableIcons = [KeyRound, Bell, Eye, Link2, LockKeyhole];
const dateTime = (value?: string | null) => value ? new Date(value).toLocaleString() : "Not available";

export default function SettingsPage() {
  const router = useRouter();
  const [profile, setProfile] = useState<CurrentUser | null>(null);
  const [session, setSession] = useState<UserProfile | null>(null);
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [message, setMessage] = useState("");

  useEffect(() => {
    setSession(getStoredProfile<UserProfile>());
    fetchProfile().then((value) => {
      setProfile(value);
      setName(value.full_name);
    }).catch(() => setError("Unable to load your profile."));
  }, []);

  async function save(event: FormEvent) {
    event.preventDefault();
    try {
      setError("");
      const response = await apiClient.put<CurrentUser>("/auth/profile", { full_name: name });
      setProfile(response.data);
      setMessage("Profile updated securely.");
    } catch {
      setError("Unable to update your profile.");
    }
  }

  async function logout() {
    await logoutUser().catch(() => undefined);
    router.replace("/login");
  }

  return (
    <SecurePage title="Settings" description="Manage your profile and understand what is secured in this session.">
      {error ? <ErrorState message={error} /> :
        !profile ? <LoadingState /> :
        <div className="space-y-6">
          <section className="grid gap-5 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><UserRound className="text-primary" />Profile</CardTitle>
                <CardDescription>Your name and email are stored through the authenticated profile API.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">{profile.email}</p>
                <form onSubmit={save} className="mt-4 flex gap-2">
                  <Input aria-label="Full name" value={name} onChange={(event) => setName(event.target.value)} minLength={2} required />
                  <Button type="submit">Save profile</Button>
                </form>
                {message ? <p className="mt-2 text-sm text-emerald-600">{message}</p> : null}
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><ShieldCheck className="text-emerald-600" />Security</CardTitle>
                <CardDescription>Your authenticated session is protected by secure sign-in and token refresh.</CardDescription>
              </CardHeader>
              <CardContent>
                <p className="text-sm text-muted-foreground">For account safety, use Logout when you finish on a shared device.</p>
                <Button variant="outline" className="mt-3" onClick={logout}>Logout from this session</Button>
              </CardContent>
            </Card>
          </section>
          <section className="grid gap-5 lg:grid-cols-2">
            <Card>
              <CardHeader>
                <CardTitle className="flex items-center gap-2"><Monitor className="text-primary" />Appearance</CardTitle>
                <CardDescription>Theme preference is supported locally on this device.</CardDescription>
              </CardHeader>
              <CardContent><ThemeToggle /></CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle>Session Information</CardTitle>
                <CardDescription>Details for the authenticated session currently in use.</CardDescription>
              </CardHeader>
              <CardContent className="grid gap-2 text-sm">
                <p><span className="text-muted-foreground">Signed in as:</span> {profile.email}</p>
                <p><span className="text-muted-foreground">User ID:</span> {profile.id}</p>
                <p><span className="text-muted-foreground">Session issued:</span> {dateTime(session?.issued_at)}</p>
                <p><span className="text-muted-foreground">Session expires:</span> {dateTime(session?.expires_at)}</p>
                <p><span className="text-muted-foreground">Profile updated:</span> {dateTime(profile.updated_at)}</p>
              </CardContent>
            </Card>
          </section>
          <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-3">
            {unavailable.map((title, index) => {
              const Icon = unavailableIcons[index];
              return <Card key={title} className="opacity-80">
                <CardHeader>
                  <CardTitle className="flex items-center gap-2"><Icon className="h-4 w-4 text-muted-foreground" />{title}</CardTitle>
                  <CardDescription>This control is not yet supported by the backend, so it remains unavailable.</CardDescription>
                </CardHeader>
                <CardContent><Button disabled variant="outline">Coming soon</Button></CardContent>
              </Card>;
            })}
          </section>
          <Card className="border-destructive/30">
            <CardHeader>
              <CardTitle className="flex items-center gap-2 text-destructive"><TriangleAlert className="h-5 w-5" />Danger zone</CardTitle>
              <CardDescription>Account deletion is intentionally unavailable because no verified deletion workflow exists in the current backend.</CardDescription>
            </CardHeader>
            <CardContent><Button disabled variant="outline">Delete account unavailable</Button></CardContent>
          </Card>
        </div>}
    </SecurePage>
  );
}
