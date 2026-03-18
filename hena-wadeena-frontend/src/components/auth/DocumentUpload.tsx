import { useRef } from "react";
import { Upload, FileCheck } from "lucide-react";

import { Button } from "@/components/ui/button";
import { Label } from "@/components/ui/label";
import { useI18n } from "@/i18n/I18nProvider";

interface DocumentUploadProps {
  docType: string;
  label: string;
  uploadedFile?: File;
  onUpload: (file: File) => void;
}

export function DocumentUpload({ docType, label, uploadedFile, onUpload }: DocumentUploadProps) {
  const { t } = useI18n();
  const inputRef = useRef<HTMLInputElement>(null);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    if (file.size > 5 * 1024 * 1024) {
      alert(t("upload.fileTooLarge"));
      return;
    }

    const allowedTypes = ["image/jpeg", "image/png", "image/webp", "application/pdf"];
    if (!allowedTypes.includes(file.type)) {
      alert(t("upload.invalidType"));
      return;
    }

    onUpload(file);
  };

  return (
    <div className="space-y-2">
      <Label htmlFor={`upload-${docType}`}>{label} *</Label>
      <input
        id={`upload-${docType}`}
        ref={inputRef}
        type="file"
        accept="image/jpeg,image/png,image/webp,application/pdf"
        onChange={handleFileChange}
        className="hidden"
      />

      {uploadedFile ? (
        <div className="flex items-center justify-between p-4 rounded-lg border border-primary/50 bg-primary/5">
          <div className="flex items-center gap-3">
            <FileCheck className="h-5 w-5 text-primary" />
            <div>
              <p className="text-sm font-medium">{uploadedFile.name}</p>
              <p className="text-xs text-muted-foreground">
                {(uploadedFile.size / 1024).toFixed(1)} {t("upload.kb")}
              </p>
            </div>
          </div>
          <Button type="button" variant="ghost" size="sm" onClick={() => inputRef.current?.click()}>
            {t("upload.change")}
          </Button>
        </div>
      ) : (
        <Button
          type="button"
          variant="outline"
          className="w-full h-24 border-dashed flex flex-col gap-2"
          onClick={() => inputRef.current?.click()}
        >
          <Upload className="h-6 w-6 text-muted-foreground" />
          <span className="text-sm text-muted-foreground">{t("upload.clickToUpload", { label })}</span>
          <span className="text-xs text-muted-foreground">{t("upload.allowed")}</span>
        </Button>
      )}
    </div>
  );
}
