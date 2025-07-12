import React from 'react';
import { Brain, Shield } from 'lucide-react';

const Header: React.FC = () => {
  return (
    <header className="bg-card border-b border-border">
      <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8">
        <div className="flex items-center justify-between h-16">
          <div className="flex items-center space-x-3">
            <div className="w-10 h-10 bg-primary rounded-lg flex items-center justify-center">
              <Brain className="w-6 h-6 text-primary-foreground" />
            </div>
            <div>
              <h1 className="text-xl font-bold text-foreground">BrainScan AI</h1>
              <p className="text-sm text-muted-foreground">MRI Tumor Detection</p>
            </div>
          </div>
          
          <div className="flex items-center space-x-2 text-sm text-muted-foreground">
            <Shield className="w-4 h-4" />
            <span>HIPAA Compliant</span>
          </div>
        </div>
      </div>
    </header>
  );
};

export default Header;