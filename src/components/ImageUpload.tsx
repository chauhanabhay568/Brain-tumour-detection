import React, { useEffect, useState } from "react";
import { X } from "lucide-react";

interface ImageUploadProps {
  onImageSelect: (file: File) => void;
  onImageRemove: () => void;
  selectedImage: File | null;
  isLoading: boolean;
}

export default function ImageUpload({
  onImageSelect,
  onImageRemove,
  selectedImage,
  isLoading,
}: ImageUploadProps) {
  const [previewUrl, setPreviewUrl] = useState<string | null>(null);

  useEffect(() => {
    if (selectedImage) {
      const url = URL.createObjectURL(selectedImage);
      setPreviewUrl(url);
      return () => URL.revokeObjectURL(url);
    } else {
      setPreviewUrl(null);
    }
  }, [selectedImage]);

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onImageSelect(file);
    }
  };

  return (
    <div className="space-y-4">
      <input
        type="file"
        accept="image/*"
        onChange={handleFileChange}
        disabled={isLoading}
        className="block w-full text-sm text-muted-foreground file:mr-4 file:py-2 file:px-4 file:border file:rounded-lg file:text-sm file:font-semibold file:bg-primary/10 file:text-primary hover:file:bg-primary/20"
      />

      {previewUrl && (
        <div className="relative mt-4">
          <img
            src={previewUrl}
            alt="Selected MRI"
            className="rounded-lg shadow w-full max-w-md mx-auto"
          />
          <button
            onClick={onImageRemove}
            disabled={isLoading}
            className="absolute top-2 right-2 bg-white text-red-500 rounded-full p-1 shadow hover:bg-red-100"
          >
            <X className="w-4 h-4" />
          </button>
        </div>
      )}
    </div>
  );
}