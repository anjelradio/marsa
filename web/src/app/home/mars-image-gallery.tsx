"use client";

import { useEffect, useState } from "react";
import Image from "next/image";
import { ChevronLeft, ChevronRight, ExternalLink, Images } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card } from "@/components/ui/card";
import type { MarsCoordinates } from "@/features/mars/infrastructure/mars-climate";
import {
  requestMarsImages,
  type MarsImage,
  type MarsImageView,
} from "@/features/mars/infrastructure/mars-images";
import { useTranslation } from "@/i18n/context";

const views = ["regional", "detail"] as const;

async function preparePreview(photo: MarsImage, signal: AbortSignal) {
  if (signal.aborted) return null;

  const preview = new window.Image();
  preview.referrerPolicy = "no-referrer";
  const cancel = () => preview.removeAttribute("src");
  signal.addEventListener("abort", cancel, { once: true });
  preview.src = photo.preview_url;

  try {
    await preview.decode();
    return photo;
  } catch {
    return null;
  } finally {
    signal.removeEventListener("abort", cancel);
  }
}

export function MarsImageGallery({ point }: { point: MarsCoordinates }) {
  const { dict } = useTranslation();
  const copy = dict.mars.images;
  const [view, setView] = useState<MarsImageView>("regional");
  const [gallery, setGallery] = useState<{ view: MarsImageView; photos: MarsImage[] } | null>(null);
  const [error, setError] = useState<"request" | "preview" | "empty" | null>(null);
  const [attempt, setAttempt] = useState(0);
  const { latitude, longitude } = point;

  useEffect(() => {
    const controller = new AbortController();
    const { signal } = controller;

    async function loadGallery() {
      const response = await requestMarsImages({ latitude, longitude }, view, signal, copy.error);
      if (signal.aborted) return;
      if (!response.ok) {
        setError("request");
        return;
      }

      const previews = await Promise.all(response.data.map((photo) => preparePreview(photo, signal)));
      if (signal.aborted) return;
      const photos = previews.filter((photo) => photo !== null);
      if (!photos.length) {
        setError(response.data.length ? "preview" : "empty");
        return;
      }

      setGallery({ view, photos });
      setError(null);
    }

    void loadGallery();
    return () => controller.abort();
  }, [latitude, longitude, view, attempt, copy.error]);

  if (!gallery && !error) return null;

  return (
    <aside aria-labelledby="mars-gallery-title" className="min-w-0 rounded-3xl max-sm:order-last sm:col-start-1 sm:row-start-1 lg:col-start-1">
      <Card className="gap-3 rounded-3xl border border-[#ffab57]/25 bg-linear-to-br from-[#302016]/95 to-[#110c0a]/95 p-4 text-white shadow-2xl backdrop-blur-md">
        <h2 id="mars-gallery-title" className="flex items-center gap-2 text-base font-medium text-white">
          <Images aria-hidden="true" className="size-4 shrink-0 text-[#ffab57]" />
          {copy.title}
        </h2>

        <div
          role="group"
          aria-label={copy.selectView}
          className="grid grid-cols-2 gap-0.5 rounded-xl border border-white/10 bg-black/35 p-0.5"
        >
          {views.map((option) => (
            <Button
              key={option}
              type="button"
              variant="ghost"
              size="sm"
              aria-pressed={(gallery?.view ?? view) === option}
              onClick={() => {
                if (option === view) return;
                setError(null);
                setView(option);
              }}
              className="h-auto min-h-8 rounded-[0.6rem] px-1.5 py-1.5 text-center text-xs whitespace-normal text-white/80 hover:bg-white/10 hover:text-white aria-pressed:bg-[#ffab57]/15 aria-pressed:text-[#ffd1a4]"
            >
              {copy.views[option]}
            </Button>
          ))}
        </div>

        {gallery && <MarsImageCarousel key={gallery.view} photos={gallery.photos} />}
        {error && (
          <div role="status" className="space-y-2">
            <p className="text-sm text-white/80">
              {error === "request" ? copy.error : error === "preview" ? copy.previewError : copy.empty}
            </p>
            {error !== "empty" && (
              <Button
                type="button"
                variant="outline"
                size="sm"
                className="rounded-full border-white/20 bg-white/5 text-white hover:bg-white/15 hover:text-white"
                onClick={() => {
                  setError(null);
                  setAttempt((previous) => previous + 1);
                }}
              >
                {copy.retry}
              </Button>
            )}
          </div>
        )}
      </Card>
    </aside>
  );
}

function MarsImageCarousel({ photos }: { photos: MarsImage[] }) {
  const { dict } = useTranslation();
  const copy = dict.mars.images;
  const [index, setIndex] = useState(0);
  const [failedPhoto, setFailedPhoto] = useState<string | null>(null);
  const active = index % photos.length;
  const photo = photos[active];
  const source = copy.sources[photo.source];
  const arrowStyle = "rounded-full border border-white/10 bg-white/5 text-white hover:bg-white/15 hover:text-white";

  return (
    <figure className="overflow-hidden rounded-2xl border border-white/10 bg-black/40">
      <div className="relative aspect-square bg-black/60">
        {failedPhoto === photo.id ? (
          <p className="grid h-full place-items-center px-3 text-center text-xs text-white/75">
            {copy.previewError}
          </p>
        ) : (
          <a
            href={photo.preview_url}
            target="_blank"
            rel="noreferrer"
            aria-label={`${copy.openPreview} · ${source} · ${photo.id}`}
            className="group absolute inset-0 focus-visible:outline-2 focus-visible:-outline-offset-2 focus-visible:outline-[#ffab57]"
          >
            <Image
              key={photo.id}
              src={photo.preview_url}
              alt={source}
              fill
              unoptimized
              onError={() => setFailedPhoto(photo.id)}
              referrerPolicy="no-referrer"
              className="object-contain"
            />
            <ExternalLink aria-hidden="true" className="absolute top-2 right-2 size-7 rounded-full bg-black/70 p-1.5 text-white group-hover:text-[#ffab57]" />
          </a>
        )}
      </div>

      <figcaption className="flex items-center justify-between gap-2 border-t border-white/10 px-3 py-2.5">
        <div className="min-w-0" aria-live="polite">
          <span className="block text-xs font-medium leading-snug text-[#ffbd80]">{source}</span>
          {photo.source !== "Viking" && (
            <span className="mt-1 block break-all font-mono text-[0.65rem] text-white/70">{photo.id}</span>
          )}
        </div>
        {photos.length > 1 && (
          <div className="flex shrink-0 items-center gap-1">
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              aria-label={copy.previous}
              className={arrowStyle}
              onClick={() => setIndex((active + photos.length - 1) % photos.length)}
            >
              <ChevronLeft aria-hidden="true" />
            </Button>
            <span aria-live="polite" className="font-mono text-[0.65rem] text-white/70">
              {active + 1}/{photos.length}
            </span>
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              aria-label={copy.next}
              className={arrowStyle}
              onClick={() => setIndex((active + 1) % photos.length)}
            >
              <ChevronRight aria-hidden="true" />
            </Button>
          </div>
        )}
      </figcaption>
    </figure>
  );
}
