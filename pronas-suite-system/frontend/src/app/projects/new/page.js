// src/app/projects/new/page.js
'use client';

import { useState } from 'react';
import { Button } from '@/components/ui/Button';
import { Card } from '@/components/ui/Card';
import { Input } from '@/components/ui/Input';

export default function NewProjectPage() {
  const [file, setFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleFileChange = (e) => {
    const selectedFile = e.target.files?.[0];
    if (selectedFile && selectedFile.type === "application/pdf") {
      setFile(selectedFile);
      setError(null);
    } else {
      setFile(null);
      setError("Por favor, selecione um arquivo PDF.");
    }
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      setError('Por favor, selecione um arquivo PDF para continuar.');
      return;
    }

    setIsLoading(true);
    setError(null);
    setAnalysisResult(null);
    const formData = new FormData();
    formData.append('file', file);

    try {
      const response = await fetch(`${process.env.NEXT_PUBLIC_API_URL}/ai/analyze-document`, {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        const errorData = await response.json();
        throw new Error(errorData.detail || 'Falha na análise do documento');
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6 text-gray-800">Gerar Projeto com IA</h1>
      <Card>
        <form onSubmit={handleSubmit}>
          <div className="mb-4">
            <label htmlFor="document" className="block text-gray-700 font-semibold mb-2">
              Anexar Documento do Projeto (PDF)
            </label>
            <Input
              type="file"
              id="document"
              accept=".pdf"
              onChange={handleFileChange}
              disabled={isLoading}
            />
             {error && <p className="text-red-500 text-sm mt-2">{error}</p>}
          </div>
          <Button type="submit" disabled={isLoading || !file} className="w-full">
            {isLoading ? 'Analisando...' : 'Analisar e Gerar Rascunho'}
          </Button>
        </form>
      </Card>

      {analysisResult && (
        <Card className="mt-8">
          <h2 className="text-xl font-semibold mb-4">Resultado da Análise</h2>
          <div className="bg-gray-50 p-4 rounded">
            <pre className="whitespace-pre-wrap text-sm text-gray-700">
              {JSON.stringify(analysisResult, null, 2)}
            </pre>
          </div>
        </Card>
      )}
    </div>
  );
}