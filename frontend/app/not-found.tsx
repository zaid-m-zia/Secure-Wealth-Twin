import Link from "next/link";

import { ArrowLeft, ShieldAlert } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

export default function NotFound() {
  return (
    <main className="flex min-h-screen items-center justify-center px-4 py-12 sm:px-6">
      <Card className="max-w-lg text-center">
        <CardHeader className="items-center">
          <div className="flex h-14 w-14 items-center justify-center rounded-2xl bg-primary/10 text-primary">
            <ShieldAlert className="h-6 w-6" />
          </div>
          <CardTitle className="mt-4 text-2xl">Page not found</CardTitle>
          <CardDescription>
            The requested route does not exist yet. Return to the platform shell and continue from there.
          </CardDescription>
        </CardHeader>
        <CardContent>
          <Button asChild className="gap-2">
            <Link href="/">
              <ArrowLeft className="h-4 w-4" />
              Go home
            </Link>
          </Button>
        </CardContent>
      </Card>
    </main>
  );
}
