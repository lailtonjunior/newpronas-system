// src/app/projects/new/page.js
'use client';

import { useState } from 'react';

export default function NewProject() {
  const [file, setFile] = useState(null);
  const [analysisResult, setAnalysisResult] = useState(null);
  const [isLoading, setIsLoading] = useState(false);

  const handleFileChange = (e) => {
    setFile(e.target.files[0]);
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!file) {
      alert('Por favor, selecione um arquivo.');
      return;
    }

    setIsLoading(true);
    const formData = new FormData();
    formData.append('file', file);

    try {
      // A URL deve apontar para o seu API Gateway (Kong), que redireciona para o AI-Service
      const response = await fetch('http://localhost:8080/ai/analyze-document', {
        method: 'POST',
        body: formData,
      });

      if (!response.ok) {
        throw new Error('Falha na análise do documento');
      }

      const result = await response.json();
      setAnalysisResult(result);
    } catch (error) {
      console.error(error);
      alert(error.message);
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="container mx-auto p-8">
      <h1 className="text-3xl font-bold mb-6">Gerar Projeto com IA</h1>
      <form onSubmit={handleSubmit} className="bg-white p-6 rounded-lg shadow-md">
        <div className="mb-4">
          <label htmlFor="document" className="block text-gray-700 font-semibold mb-2">
            Anexar Documento do Projeto (PDF)
          </label>
          <input
            type="file"
            id="document"
            accept=".pdf"
            onChange={handleFileChange}
            className="w-full p-2 border rounded"
          />
        </div>
        <button
          type="submit"
          disabled={isLoading}
          className="w-full bg-blue-600 text-white py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
        >
          {isLoading ? 'Analisando...' : 'Analisar e Gerar Projeto'}
        </button>
      </form>

      {analysisResult && (
        <div className="mt-8 bg-gray-100 p-6 rounded-lg">
          <h2 className="text-xl font-semibold mb-4">Resultado da Análise</h2>
          <pre className="whitespace-pre-wrap">{JSON.stringify(analysisResult, null, 2)}</pre>
        </div>
      )}
    </div>
  );
}
