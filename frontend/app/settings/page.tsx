"use client";
import { FormEvent, useEffect, useState } from "react";
import { ErrorState, LoadingState } from "@/components/data-state";
import { SecurePage } from "@/components/secure-page";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { fetchProfile, logoutUser } from "@/services/auth";
import { apiClient } from "@/services/api";
import { useRouter } from "next/navigation";
export default function SettingsPage() { const router = useRouter(); const [profile, setProfile] = useState<{ full_name: string; email: string } | null>(null); const [name, setName] = useState(""); const [error, setError] = useState(""); const [message, setMessage] = useState(""); useEffect(() => { fetchProfile().then((value) => { setProfile(value as typeof profile); setName(value.full_name ?? ""); }).catch(() => setError("Unable to load your profile.")); }, []); async function save(event: FormEvent) { event.preventDefault(); try { const response = await apiClient.put("/auth/profile", { full_name: name }); setProfile(response.data); setMessage("Profile updated."); } catch { setError("Unable to update your profile."); } } async function logout() { await logoutUser().catch(() => undefined); router.replace("/login"); } return <SecurePage title="Profile & Settings" description="Manage the current user and secure session.">{error ? <ErrorState message={error}/> : !profile ? <LoadingState/> : <Card><CardHeader><CardTitle>Your profile</CardTitle></CardHeader><CardContent><p className="text-sm text-muted-foreground">{profile.email}</p><form onSubmit={save} className="mt-5 flex flex-col gap-3 sm:flex-row"><Input value={name} onChange={(event) => setName(event.target.value)} minLength={2} required/><Button type="submit">Save profile</Button><Button variant="outline" onClick={logout}>Logout</Button></form>{message ? <p className="text-sm text-success">{message}</p> : null}</CardContent></Card>}</SecurePage>; }
