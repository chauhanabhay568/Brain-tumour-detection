import React from 'react';
import { CheckCircle, AlertTriangle, Info, Clock } from 'lucide-react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Badge } from '@/components/ui/badge';
import { Alert, AlertDescription } from '@/components/ui/alert';

interface DiagnosisResultProps {
  result: {
    prediction: 'tumor' | 'no_tumor';
    confidence: number;
    processingTime?: number;
  } | null;
  isLoading: boolean;
}

const DiagnosisResult: React.FC<DiagnosisResultProps> = ({ result, isLoading }) => {
  if (isLoading) {
    return (
      <Card className="border-primary/20">
        <CardContent className="p-8">
          <div className="text-center space-y-4">
            <div className="w-16 h-16 mx-auto bg-primary/10 rounded-full flex items-center justify-center">
              <Clock className="w-8 h-8 text-primary animate-pulse" />
            </div>
            <div className="space-y-2">
              <h3 className="text-lg font-semibold text-foreground">Analyzing MRI Scan</h3>
              <p className="text-muted-foreground">
                Our AI model is processing your image. This may take a few moments...
              </p>
            </div>
            <div className="w-32 h-2 bg-muted rounded-full mx-auto overflow-hidden">
              <div className="h-full bg-primary rounded-full animate-pulse" style={{ width: '60%' }}></div>
            </div>
          </div>
        </CardContent>
      </Card>
    );
  }

  if (!result) {
    return (
      <Card className="border-dashed border-border">
        <CardContent className="p-8">
          <div className="text-center space-y-2">
            <Info className="w-12 h-12 mx-auto text-muted-foreground" />
            <h3 className="text-lg font-medium text-muted-foreground">Upload an image to get started</h3>
            <p className="text-sm text-muted-foreground">
              Your diagnosis results will appear here
            </p>
          </div>
        </CardContent>
      </Card>
    );
  }

  const isTumor = result.prediction === 'tumor';
  const confidencePercent = Math.round(result.confidence * 100);

  return (
    <div className="space-y-4">
      <Card className={`border-2 ${isTumor ? 'border-warning/30 bg-warning/5' : 'border-success/30 bg-success/5'}`}>
        <CardHeader className="pb-3">
          <div className="flex items-center justify-between">
            <CardTitle className="flex items-center gap-3">
              {isTumor ? (
                <AlertTriangle className="w-6 h-6 text-warning" />
              ) : (
                <CheckCircle className="w-6 h-6 text-success" />
              )}
              Diagnosis Result
            </CardTitle>
            <Badge 
              variant={isTumor ? "secondary" : "default"}
              className={isTumor ? "bg-warning/10 text-warning border-warning/20" : "bg-success/10 text-success border-success/20"}
            >
              {confidencePercent}% confidence
            </Badge>
          </div>
        </CardHeader>
        
        <CardContent className="space-y-4">
          <div className="text-center space-y-2">
            <h3 className={`text-2xl font-bold ${isTumor ? 'text-warning' : 'text-success'}`}>
              {isTumor ? 'Potential Tumor Detected' : 'No Tumor Detected'}
            </h3>
            <p className="text-muted-foreground">
              {isTumor 
                ? 'The AI model has identified potential abnormalities that may indicate a tumor.'
                : 'The AI model did not detect any signs of tumor in this MRI scan.'
              }
            </p>
          </div>

          <div className="pt-2">
            <div className="flex justify-between text-sm text-muted-foreground mb-2">
              <span>Confidence Level</span>
              <span>{confidencePercent}%</span>
            </div>
            <div className="w-full bg-muted rounded-full h-2">
              <div 
                className={`h-2 rounded-full transition-all duration-1000 ${
                  isTumor ? 'bg-warning' : 'bg-success'
                }`}
                style={{ width: `${confidencePercent}%` }}
              />
            </div>
          </div>

          {result.processingTime && (
            <div className="text-center text-sm text-muted-foreground">
              Analysis completed in {result.processingTime}s
            </div>
          )}
        </CardContent>
      </Card>

      <Alert>
        <Info className="h-4 w-4" />
        <AlertDescription>
          <strong>Important Medical Disclaimer:</strong> This AI tool is for educational and screening purposes only. 
          It should not replace professional medical consultation, diagnosis, or treatment. Please consult with a 
          qualified healthcare provider for proper medical evaluation and interpretation of your MRI results.
        </AlertDescription>
      </Alert>
    </div>
  );
};

export default DiagnosisResult;