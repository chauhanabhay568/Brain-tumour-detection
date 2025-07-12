import React, { useState } from 'react';
import { Zap, Upload as UploadIcon } from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { useToast } from '@/hooks/use-toast';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import ImageUpload from '@/components/ImageUpload';
import DiagnosisResult from '@/components/DiagnosisResult';

interface DiagnosisResult {
  prediction: 'tumor' | 'no_tumor';
  confidence: number;
  processingTime?: number;
}

const Index = () => {
  const [selectedImage, setSelectedImage] = useState<File | null>(null);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState<DiagnosisResult | null>(null);
  const { toast } = useToast();

  const handleImageSelect = (file: File) => {
    // Validate file size (10MB limit)
    if (file.size > 10 * 1024 * 1024) {
      toast({
        title: "File too large",
        description: "Please select an image smaller than 10MB.",
        variant: "destructive",
      });
      return;
    }

    setSelectedImage(file);
    setResult(null); // Clear previous results
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

    setIsLoading(true);
    const startTime = Date.now();

    try {
      // Simulate API call to backend model
      // In a real application, you would send the image to your ML backend
      await new Promise(resolve => setTimeout(resolve, 3000)); // Simulate processing time
      
      const endTime = Date.now();
      const processingTime = ((endTime - startTime) / 1000).toFixed(1);

      // Mock result - in real app, this would come from your backend
      const mockResult: DiagnosisResult = {
        prediction: Math.random() > 0.7 ? 'tumor' : 'no_tumor',
        confidence: 0.85 + Math.random() * 0.14, // 85-99% confidence
        processingTime: parseFloat(processingTime)
      };

      setResult(mockResult);
      
      toast({
        title: "Analysis complete",
        description: `Diagnosis completed in ${processingTime}s`,
      });
    } catch (error) {
      toast({
        title: "Analysis failed",
        description: "There was an error processing your image. Please try again.",
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
              Upload your MRI scan for fast, accurate analysis using advanced machine learning. 
              Get preliminary results in seconds to support your healthcare decisions.
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

          {/* Features Section */}
          <div className="mt-16 grid md:grid-cols-3 gap-6">
            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <Zap className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">Fast Analysis</h3>
                <p className="text-sm text-muted-foreground">
                  Get results in seconds with our optimized AI model
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <UploadIcon className="w-6 h-6 text-primary" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">Easy Upload</h3>
                <p className="text-sm text-muted-foreground">
                  Simple drag-and-drop interface for all image formats
                </p>
              </CardContent>
            </Card>

            <Card className="text-center">
              <CardContent className="p-6">
                <div className="w-12 h-12 bg-primary/10 rounded-lg flex items-center justify-center mx-auto mb-4">
                  <div className="w-6 h-6 bg-primary rounded-full" />
                </div>
                <h3 className="font-semibold text-foreground mb-2">High Accuracy</h3>
                <p className="text-sm text-muted-foreground">
                  Advanced neural networks trained on medical datasets
                </p>
              </CardContent>
            </Card>
          </div>
        </div>
      </main>

      <Footer />
    </div>
  );
};

export default Index;
