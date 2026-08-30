"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FileTextIcon,
  LayoutDashboardIcon,
  MessageSquareIcon,
  ScaleIcon,
  TestTubeIcon,
} from "lucide-react";

import { cn } from "@/lib/utils";

const links = [
  { href: "/tableau-de-bord", label: "Tableau de bord", icon: LayoutDashboardIcon },
  { href: "/analyser", label: "Analyser", icon: MessageSquareIcon },
  { href: "/simulation", label: "Simulation", icon: TestTubeIcon },
  { href: "/audit", label: "Audit", icon: ScaleIcon },
  { href: "/fiche-modele", label: "Fiche modèle", icon: FileTextIcon },
];

export function AppNavigation() {
  const pathname = usePathname();

  return (
    <header className="sticky top-0 z-40 border-b border-border bg-background/95 backdrop-blur">
      <div className="app-section flex items-center justify-between gap-4 py-4">
        <Link
          href="/tableau-de-bord"
          className="text-title font-bold tracking-tight"
        >
          Gardien de Contenu IA
        </Link>
        <nav className="flex items-center gap-1 overflow-x-auto">
          {links.map((link) => {
            const isActive = pathname === link.href;
            const Icon = link.icon;
            return (
              <Link
                key={link.href}
                href={link.href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-3 py-2 text-small font-medium transition-colors whitespace-nowrap",
                  isActive
                    ? "bg-background-100 text-foreground"
                    : "text-muted-foreground hover:bg-background-100 hover:text-foreground",
                )}
                data-cy={`nav-${link.href.replace("/", "")}`}
              >
                <Icon className="size-4" />
                {link.label}
              </Link>
            );
          })}
        </nav>
      </div>
    </header>
  );
}
