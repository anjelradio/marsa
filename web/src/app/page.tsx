"use client";

import Link from "next/link";
import { LandingHeader } from "@/features/shared/presentation/components/layout/landing-header";
import {
  Card,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Separator } from "@/components/ui/separator";
import { Button } from "@/components/ui/button";
import { useTranslation } from "@/i18n/context";
import { Rocket } from "lucide-react";

export default function Home() {
  const { dict } = useTranslation();

  return (
    <div className="flex min-h-screen flex-col bg-background">
      <LandingHeader />

      <main className="flex flex-1 flex-col items-center px-6 py-16">
        <div className="mx-auto w-full max-w-3xl space-y-12">
          {/* Hero */}
          <section className="space-y-5 text-center">
            <div className="mx-auto w-fit rounded-full border border-border bg-muted px-4 py-1.5 text-xs font-medium text-muted-foreground">
              {dict.landing.badge}
            </div>
            <h1 className="text-4xl font-bold tracking-tight sm:text-5xl font-headline">
              {dict.landing.heroTitle}
            </h1>
            <p className="mx-auto max-w-xl text-lg leading-relaxed text-muted-foreground">
              {dict.landing.heroSubtitle}
            </p>

            <div className="pt-2">
              <Button asChild size="lg" className="rounded-full shadow-md gap-2 font-medium">
                <Link href="/home">
                  <Rocket className="size-4" />
                  {dict.landing.viewDashboard}
                </Link>
              </Button>
            </div>
          </section>

          <Separator />

          {/* Tech Stack */}
          <section className="space-y-6">
            <h2 className="text-center text-xl font-semibold tracking-tight font-headline">
              {dict.landing.featuresTitle}
            </h2>

            <div className="grid gap-4 sm:grid-cols-2">
              <Card>
                <CardHeader>
                  <CardTitle>{dict.landing.nextjsTitle}</CardTitle>
                  <CardDescription>
                    {dict.landing.nextjsDesc}
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>{dict.landing.authTitle}</CardTitle>
                  <CardDescription>
                    {dict.landing.authDesc}
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>{dict.landing.shadcnTitle}</CardTitle>
                  <CardDescription>
                    {dict.landing.shadcnDesc}
                  </CardDescription>
                </CardHeader>
              </Card>

              <Card>
                <CardHeader>
                  <CardTitle>{dict.landing.cleanArchTitle}</CardTitle>
                  <CardDescription>
                    {dict.landing.cleanArchDesc}
                  </CardDescription>
                </CardHeader>
              </Card>
            </div>
          </section>

          <Separator />

          {/* Explore */}
          <section className="space-y-4 text-center">
            <h2 className="text-xl font-semibold tracking-tight font-headline">
              {dict.landing.exploreTitle}
            </h2>
            <p className="mx-auto max-w-lg text-sm leading-relaxed text-muted-foreground">
              {dict.landing.exploreDesc}
            </p>
          </section>
        </div>
      </main>

      {/* Footer */}
      <footer className="border-t border-border/40 py-6 text-center text-xs text-muted-foreground">
        {dict.landing.footer}
      </footer>
    </div>
  );
}
