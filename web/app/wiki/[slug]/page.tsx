"use client";

import { useEffect, useState } from "react";
import Link from "next/link";
import { ArrowLeft, BookOpen } from "lucide-react";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { apiGet } from "@/lib/api";

interface WikiArticle {
  slug: string;
  title: string;
  category: string;
  tags: string[];
  body: string;
}

export default function WikiArticlePage({
  params,
}: {
  params: { slug: string };
}) {
  const slug = decodeURIComponent(params.slug);
  const [article, setArticle] = useState<WikiArticle | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    setLoading(true);
    apiGet<WikiArticle>(`/api/wiki/article/${encodeURIComponent(slug)}`)
      .then(setArticle)
      .catch((e) => setError(e instanceof Error ? e.message : "Failed to load"))
      .finally(() => setLoading(false));
  }, [slug]);

  if (loading) {
    return (
      <div className="mx-auto max-w-3xl space-y-6">
        <Skeleton className="h-8 w-64" />
        <Skeleton className="h-96 w-full" />
      </div>
    );
  }

  if (error || !article) {
    return (
      <div className="mx-auto max-w-3xl space-y-4">
        <Link href="/wiki" className="inline-flex items-center gap-1 text-sm text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-4 w-4" /> Back to Wiki
        </Link>
        <p className="py-12 text-center text-muted-foreground">
          {error || "Article not found."}
        </p>
      </div>
    );
  }

  const paragraphs = article.body.split("\n\n");

  return (
    <div className="mx-auto max-w-3xl space-y-6">
      <div className="flex items-center gap-3">
        <Link href="/wiki" className="text-muted-foreground hover:text-foreground">
          <ArrowLeft className="h-5 w-5" />
        </Link>
        <div>
          <div className="flex items-center gap-2">
            <BookOpen className="h-5 w-5 text-primary" />
            <h1 className="text-2xl font-semibold tracking-tight">
              {article.title}
            </h1>
          </div>
          <div className="mt-1 flex flex-wrap items-center gap-2">
            <Badge variant="outline">{article.category}</Badge>
            {article.tags.map((t) => (
              <Badge
                key={t}
                variant="outline"
                className="text-[10px] text-muted-foreground"
              >
                {t}
              </Badge>
            ))}
          </div>
        </div>
      </div>

      <Card>
        <CardContent className="pt-6">
          <div className="space-y-4 text-sm leading-relaxed text-foreground/90">
            {paragraphs.map((p, i) => {
              if (p.startsWith("- ")) {
                const items = p.split("\n").filter((l) => l.startsWith("- "));
                return (
                  <ul key={i} className="list-inside list-disc space-y-1.5 pl-2">
                    {items.map((item, j) => (
                      <li key={j}>{item.slice(2)}</li>
                    ))}
                  </ul>
                );
              }
              const lines = p.split("\n");
              return (
                <div key={i}>
                  {lines.map((line, j) => {
                    if (line.startsWith("- ")) {
                      return (
                        <ul key={j} className="my-1 list-inside list-disc pl-2">
                          <li>{line.slice(2)}</li>
                        </ul>
                      );
                    }
                    return <p key={j}>{line}</p>;
                  })}
                </div>
              );
            })}
          </div>
        </CardContent>
      </Card>

      <div className="flex justify-center">
        <Link
          href="/wiki"
          className="text-sm text-muted-foreground hover:text-foreground"
        >
          &larr; Back to all articles
        </Link>
      </div>
    </div>
  );
}
