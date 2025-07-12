import React from 'react';
import { Heart, Shield, Clock } from 'lucide-react';

const Footer: React.FC = () => {
  return (
    <footer className="bg-card border-t border-border">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
          <div className="text-center md:text-left">
            <div className="flex items-center justify-center md:justify-start space-x-2 mb-2">
              <Heart className="w-5 h-5 text-primary" />
              <span className="font-semibold text-foreground">Healthcare Technology</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Advancing medical diagnosis through artificial intelligence
            </p>
          </div>
          
          <div className="text-center">
            <div className="flex items-center justify-center space-x-2 mb-2">
              <Shield className="w-5 h-5 text-primary" />
              <span className="font-semibold text-foreground">Privacy & Security</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Your medical data is processed securely and not stored
            </p>
          </div>
          
          <div className="text-center md:text-right">
            <div className="flex items-center justify-center md:justify-end space-x-2 mb-2">
              <Clock className="w-5 h-5 text-primary" />
              <span className="font-semibold text-foreground">24/7 Available</span>
            </div>
            <p className="text-sm text-muted-foreground">
              Fast, reliable AI-powered analysis anytime
            </p>
          </div>
        </div>
        
        <div className="mt-6 pt-6 border-t border-border text-center">
          <p className="text-sm text-muted-foreground">
            © 2024 BrainScan AI. This tool is for educational purposes only. 
            Always consult healthcare professionals for medical decisions.
          </p>
        </div>
      </div>
    </footer>
  );
};

export default Footer;