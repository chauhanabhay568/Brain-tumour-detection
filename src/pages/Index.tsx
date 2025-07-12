import React, { useState } from "react";
import { Zap, Upload as UploadIcon } from "lucide-react";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { useToast } from "@/hooks/use-toast";
import Header from "@/components/Header";
import Footer from "@/components/Footer";
import ImageUpload from "@/components/ImageUpload";
import DiagnosisResult from "@/components/DiagnosisResult";

interface DiagnosisResult {
  prediction: "tumor" | "no_tumor";
  confidence: number;
  processingTime?: number;
}

const Index = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const { toast } = useToast();

  const handleImageSelect = (file: File) => {
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please select an image smaller than 10MB.",
        variant: "destructive",
      });
      return;
    }

    setSelectedImage(file);
    setResult(null);
    toast({
      title: "Image selected",
      description: `${file.name} is ready for analysis.`,
    });
  };

  const handleImageRemove = () => {
    setSelectedImage(null);
    setResult(null);
    toast({
      title: "Image removed",
      description: "Upload a new image to get started.",
    });
  };

  const handleDiagnosis = async () => {
    if (!selectedImage) {
      toast({
        title: "No image selected",
        description: "Please upload an MRI image first.",
        variant: "destructive",
      });
      return;
    }

    const formData = new FormData();
    formData.append("file", selectedImage);

    setIsLoading(true);
    const startTime = performance.now();

    try {
      const response = await fetch("http://127.0.0.1:8000/predict/", {
        method: "POST",
        body: formData,
      });

      const data = await response.json();

      if (!response.ok || data.error) {
        throw new Error(data.error || "Unexpected server error.");
      }

      const rawPrediction = data.prediction.toLowerCase();
      const isTumor = !rawPrediction.includes("not");

      const mappedResult: DiagnosisResult = {
        prediction: isTumor ? "tumor" : "no_tumor",
        confidence: isTumor ? data.probability : 1 - data.probability,
        processingTime: Number(
          ((performance.now() - startTime) / 1000).toFixed(2)
        ),
      };

      setResult(mappedResult);

      toast({
        title: "Analysis complete",
        description: `Diagnosis completed in ${mappedResult.processingTime}s`,
      });
    } catch (error: any) {
      toast({
        title: "Analysis failed",
        description: error.message || "There was a problem.",
        variant: "destructive",
      });
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-background flex flex-col">
      <Header />

      <main className="flex-1 py-8">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
          {/* Hero Section */}
          <div className="text-center mb-12">
            <h1 className="text-4xl font-bold text-foreground mb-4">
              AI-Powered Brain Tumor Detection
            </h1>
            <p className="text-xl text-muted-foreground max-w-2xl mx-auto">
              Upload your MRI scan for fast, accurate analysis using advanced
              machine learning. Get preliminary results in seconds to support
              your healthcare decisions.
            </p>
          </div>

          <div className="grid lg:grid-cols-2 gap-8">
            {/* Upload Section */}
            <div className="space-y-6">
              <Card>
                <CardHeader>
                  <CardTitle className="flex items-center gap-2">
                    <UploadIcon className="w-5 h-5" />
                    Upload MRI Image
                  </CardTitle>
                </CardHeader>
                <CardContent>
                  <ImageUpload
                    onImageSelect={handleImageSelect}
                    onImageRemove={handleImageRemove}
                    selectedImage={selectedImage}
                    isLoading={isLoading}
                  />
                </CardContent>
              </Card>

              {selectedImage && (
                <Card>
                  <CardContent className="p-6">
                    <Button
                      onClick={handleDiagnosis}
                      disabled={isLoading || !selectedImage}
                      className="w-full h-12 text-lg"
                      size="lg"
                    >
                      {isLoading ? (
                        <>
                          <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-primary-foreground mr-2" />
                          Analyzing...
                        </>
                      ) : (
                        <>
                          <Zap className="w-5 h-5 mr-2" />
                          Get Diagnosis
                        </>
                      )}
                    </Button>
                  </CardContent>
                </Card>
              )}
            </div>

            {/* Results Section */}
            <div>
              <Card>
                <CardHeader>
                  <CardTitle>Diagnosis Results</CardTitle>
                </CardHeader>
                <CardContent>
                  <DiagnosisResult result={result} isLoading={isLoading} />
                </CardContent>
              </Card>
            </div>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Index;