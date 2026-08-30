import { Info } from "lucide-react";

interface TranslationNoticeProps {
  language: string;
  translatedText: string;
}

export function TranslationNotice({
  language,
  translatedText,
}: TranslationNoticeProps) {
  return (
    <div className="flex items-start gap-3 rounded-lg border border-background-200 bg-background-100 p-4">
      <Info className="mt-0.5 size-4 shrink-0 text-muted-foreground" />
      <div className="space-y-1">
        <p className="text-small font-medium text-foreground">
          Texte traduit automatiquement depuis {language}
        </p>
        <p className="text-small text-muted-foreground italic">
          {translatedText}
        </p>
      </div>
    </div>
  );
}
