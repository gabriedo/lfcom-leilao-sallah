import { useState } from "react";
import { Button } from "@/components/ui/button";
import { useToast } from "@/hooks/use-toast";
import { Upload, Loader2, Search, AlertCircle, ArrowLeft, ArrowRight } from "lucide-react";
import { format } from "date-fns";
import { ptBR } from "date-fns/locale";

import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { Textarea } from "@/components/ui/textarea";
import { Alert, AlertDescription } from "@/components/ui/alert";
import { Badge } from "@/components/ui/badge";
import { Separator } from "@/components/ui/separator";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";

interface FileWithPreview extends File {
  preview: string;
}

interface AnalysisResult {
  dados_imovel: {
    titulo: string;
    tipo_imovel: string;
    area_total: number;
    endereco: string;
    bairro: string;
    cidade: string;
    estado: string;
    valor_inicial: number;
    valor_atual: number;
    data_inicio: string;
    imagens: string[];
  };
  tipo_leilao: string;
  data_fim: string;
  documentos: string[];
  recomendacoes: string[];
}

interface QuickAnalysisData {
  dados_imovel: {
    titulo: string;
    tipo_imovel: string;
    area_total: number;
    endereco: string;
    bairro: string;
    cidade: string;
    estado: string;
    imagens: string[];
  };
  tipo_leilao: string;
  valor_inicial: number;
  valor_atual: number;
  data_inicio: string;
  data_fim: string;
  documentos: string[];
  recomendacoes: string[];
}

interface MissingInfo {
  propertyType: string;
  auctionType: string;
  minBid: number;
  evaluatedValue: number;
  address: string;
  auctionDate: string;
  propertyArea: number;
}

export default function AnalysisForm() {
  const { toast } = useToast();
  const [currentStep, setCurrentStep] = useState(1);
  const [loading, setLoading] = useState(false);
  const [files, setFiles] = useState<FileWithPreview[]>([]);
  const [propertyUrl, setPropertyUrl] = useState("");
  const [extracting, setExtracting] = useState(false);
  const [analysisResult, setAnalysisResult] = useState<AnalysisResult | null>(null);
  const [missingInfo, setMissingInfo] = useState<MissingInfo>({
    propertyType: '',
    auctionType: '',
    minBid: 0,
    evaluatedValue: 0,
    address: '',
    auctionDate: new Date().toISOString().split('T')[0],
    propertyArea: 0,
  });
  const [error, setError] = useState<string | null>(null);

  const handleExtractData = async () => {
    try {
      setExtracting(true);
      console.log('Iniciando extração de dados para URL:', propertyUrl);
      
      const response = await fetch(`http://localhost:5001/api/extract?url=${encodeURIComponent(propertyUrl)}`);
      console.log('Resposta recebida:', response.status);
      
      const data = await response.json();
      console.log('Dados extraídos:', data);

      if (!response.ok) {
        throw new Error(data.error || 'Erro ao extrair dados');
      }

      const formatDate = (dateString: string) => {
        if (!dateString) return new Date().toISOString().split('T')[0];
        return new Date(dateString).toISOString().split('T')[0];
      };

      const mappedData: AnalysisResult = {
        dados_imovel: {
          titulo: data.dados_imovel?.titulo || '',
          tipo_imovel: data.dados_imovel?.tipo_imovel || '',
          area_total: parseFloat(data.dados_imovel?.area_total) || 0,
          endereco: data.dados_imovel?.endereco || '',
          bairro: data.dados_imovel?.bairro || '',
          cidade: data.dados_imovel?.cidade || '',
          estado: data.dados_imovel?.estado || '',
          valor_inicial: parseFloat(data.dados_imovel?.valor_inicial) || 0,
          valor_atual: parseFloat(data.dados_imovel?.valor_atual) || 0,
          data_inicio: formatDate(data.dados_imovel?.data_inicio),
          imagens: data.dados_imovel?.imagens || []
        },
        tipo_leilao: data.tipo_leilao || '',
        data_fim: formatDate(data.data_fim),
        documentos: data.documentos || [],
        recomendacoes: data.recomendacoes || []
      };

      console.log('Dados mapeados:', mappedData);
      setAnalysisResult(mappedData);
      setCurrentStep(2);

      toast({
        title: "Dados extraídos com sucesso!",
        description: "Agora você pode complementar as informações necessárias.",
        variant: "default"
      });
    } catch (error) {
      console.error('Erro ao extrair dados:', error);
      toast({
        title: "Erro ao extrair dados",
        description: error instanceof Error ? error.message : "Ocorreu um erro ao extrair os dados do imóvel",
        variant: "destructive"
      });
    } finally {
      setExtracting(false);
    }
  };

  const handleFileChange = (event: React.ChangeEvent<HTMLInputElement>) => {
    const selectedFiles = event.target.files;
    if (selectedFiles) {
      const newFiles = Array.from(selectedFiles).map(file => {
        const fileWithPreview = file as FileWithPreview;
        fileWithPreview.preview = URL.createObjectURL(file);
        return fileWithPreview;
      });
      setFiles(prevFiles => [...prevFiles, ...newFiles]);
    }
  };

  const handleSubmit = async (e?: React.FormEvent) => {
    if (e) {
      e.preventDefault();
    }

    try {
      setLoading(true);
      
      // Preparar os dados no formato esperado pelo backend
      const requestData = {
        edital: propertyUrl,
        matricula: files.map(file => file.name).join(','),
        tipo_imovel: analysisResult?.dados_imovel.tipo_imovel || '',
        area_total: analysisResult?.dados_imovel.area_total || 0,
        endereco: analysisResult?.dados_imovel.endereco || '',
        valor_inicial: analysisResult?.dados_imovel.valor_inicial || 0,
        valor_atual: analysisResult?.dados_imovel.valor_atual || 0,
        data_inicio: analysisResult?.dados_imovel.data_inicio || new Date().toISOString(),
        documentos: files.map(file => file.name)
      };

      console.log('Enviando dados para análise:', requestData);

      const response = await fetch('http://localhost:5001/api/analyze', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(requestData)
      });

      const data = await response.json();
      console.log('Dados recebidos da API:', data);

      if (!response.ok || data.error || data.observacoes?.includes('Erro')) {
        throw new Error(data.observacoes || data.error || 'Erro ao processar análise');
      }

      // Mapear os dados recebidos para o formato esperado
      const mappedData: AnalysisResult = {
        dados_imovel: {
          titulo: analysisResult?.dados_imovel.titulo || '',
          tipo_imovel: analysisResult?.dados_imovel.tipo_imovel || '',
          area_total: analysisResult?.dados_imovel.area_total || 0,
          endereco: analysisResult?.dados_imovel.endereco || '',
          bairro: analysisResult?.dados_imovel.bairro || '',
          cidade: analysisResult?.dados_imovel.cidade || '',
          estado: analysisResult?.dados_imovel.estado || '',
          valor_inicial: analysisResult?.dados_imovel.valor_inicial || 0,
          valor_atual: analysisResult?.dados_imovel.valor_atual || 0,
          data_inicio: analysisResult?.dados_imovel.data_inicio || new Date().toISOString(),
          imagens: analysisResult?.dados_imovel.imagens || []
        },
        tipo_leilao: analysisResult?.tipo_leilao || '',
        data_fim: analysisResult?.data_fim || new Date().toISOString(),
        documentos: files.map(file => file.name),
        recomendacoes: data.recomendacoes || []
      };

      // Adicionar informações adicionais da análise
      if (data.dividas_condominio && data.dividas_condominio !== 'erro') {
        mappedData.recomendacoes.push(`Dívidas de condomínio: ${data.dividas_condominio}`);
      }
      if (data.ocupado && data.ocupado !== 'erro') {
        mappedData.recomendacoes.push(`Status de ocupação: ${data.ocupado}`);
      }
      if (data.penhora && data.penhora !== 'erro') {
        mappedData.recomendacoes.push(`Status de penhora: ${data.penhora}`);
      }
      if (data.observacoes && !data.observacoes.includes('Erro')) {
        mappedData.recomendacoes.push(data.observacoes);
      }

      console.log('Dados mapeados finais:', mappedData);
      setAnalysisResult(mappedData);
      setCurrentStep(4);

      toast({
        title: "Análise concluída com sucesso!",
        description: "Os dados foram processados e estão prontos para visualização.",
        variant: "default"
      });
    } catch (error) {
      console.error('Erro ao analisar o imóvel:', error);
      toast({
        title: "Erro ao processar análise",
        description: error instanceof Error ? error.message : "Ocorreu um erro ao processar a análise. Por favor, tente novamente.",
        variant: "destructive"
      });
    } finally {
      setLoading(false);
    }
  };

  const renderStep = () => {
    switch (currentStep) {
      case 1:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Análise de Imóvel</CardTitle>
              <CardDescription>
                Cole a URL do imóvel para iniciar a análise
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="space-y-2">
                  <Label htmlFor="url">URL do Imóvel</Label>
                  <div className="flex space-x-2">
                    <Input
                      id="url"
                      value={propertyUrl}
                      onChange={(e) => setPropertyUrl(e.target.value)}
                      placeholder="https://www.exemplo.com/imovel/123"
                      className="flex-1"
                    />
                    <Button
                      onClick={handleExtractData}
                      disabled={!propertyUrl || extracting}
                    >
                      {extracting ? (
                        <>
                          <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                          Extraindo...
                        </>
                      ) : (
                        <>
                          <Search className="mr-2 h-4 w-4" />
                          Extrair Dados
                        </>
                      )}
                    </Button>
                  </div>
                </div>
              </div>
            </CardContent>
          </Card>
        );
      case 2:
        return (
          <div className="space-y-6">
            {analysisResult && (
              <Card>
                <CardHeader>
                  <CardTitle>Dados do Imóvel</CardTitle>
                  <CardDescription>
                    Informações extraídas do anúncio
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="space-y-4">
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Tipo de Imóvel</Label>
                        <Select
                          value={analysisResult.dados_imovel.tipo_imovel}
                          onValueChange={(value) => {
                            setAnalysisResult(prev => prev ? {
                              ...prev,
                              dados_imovel: {
                                ...prev.dados_imovel,
                                tipo_imovel: value
                              }
                            } : null);
                          }}
                        >
                          <SelectTrigger>
                            <SelectValue placeholder="Selecione o tipo" />
                          </SelectTrigger>
                          <SelectContent>
                            <SelectItem value="apartamento">Apartamento</SelectItem>
                            <SelectItem value="casa">Casa</SelectItem>
                            <SelectItem value="terreno">Terreno</SelectItem>
                            <SelectItem value="comercial">Comercial</SelectItem>
                          </SelectContent>
                        </Select>
                      </div>
                      <div>
                        <Label>Área Total (m²)</Label>
                        <Input
                          type="number"
                          value={analysisResult.dados_imovel.area_total}
                          onChange={(e) => {
                            setAnalysisResult(prev => prev ? {
                              ...prev,
                              dados_imovel: {
                                ...prev.dados_imovel,
                                area_total: parseFloat(e.target.value)
                              }
                            } : null);
                          }}
                        />
                      </div>
                    </div>
                    <div className="grid grid-cols-2 gap-4">
                      <div>
                        <Label>Valor Inicial</Label>
                        <Input
                          type="number"
                          value={analysisResult.dados_imovel.valor_inicial}
                          onChange={(e) => {
                            setAnalysisResult(prev => prev ? {
                              ...prev,
                              dados_imovel: {
                                ...prev.dados_imovel,
                                valor_inicial: parseFloat(e.target.value)
                              }
                            } : null);
                          }}
                        />
                      </div>
                      <div>
                        <Label>Valor Atual</Label>
                        <Input
                          type="number"
                          value={analysisResult.dados_imovel.valor_atual}
                          onChange={(e) => {
                            setAnalysisResult(prev => prev ? {
                              ...prev,
                              dados_imovel: {
                                ...prev.dados_imovel,
                                valor_atual: parseFloat(e.target.value)
                              }
                            } : null);
                          }}
                        />
                      </div>
                    </div>
                    <div>
                      <Label>Data do Leilão</Label>
                      <Input
                        type="date"
                        value={analysisResult.dados_imovel.data_inicio}
                        onChange={(e) => {
                          setAnalysisResult(prev => prev ? {
                            ...prev,
                            dados_imovel: {
                              ...prev.dados_imovel,
                              data_inicio: e.target.value
                            }
                          } : null);
                        }}
                      />
                    </div>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        );
      case 3:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Documentos</CardTitle>
              <CardDescription>
                Adicione os documentos necessários para a análise
              </CardDescription>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                <div className="flex items-center justify-center w-full">
                  <label
                    htmlFor="dropzone-file"
                    className="flex flex-col items-center justify-center w-full h-64 border-2 border-gray-300 border-dashed rounded-lg cursor-pointer bg-gray-50 hover:bg-gray-100"
                  >
                    <div className="flex flex-col items-center justify-center pt-5 pb-6">
                      <Upload className="w-8 h-8 mb-4 text-gray-500" />
                      <p className="mb-2 text-sm text-gray-500">
                        <span className="font-semibold">Clique para enviar</span> ou arraste e solte
                      </p>
                      <p className="text-xs text-gray-500">PDF, DOC, DOCX, JPG, PNG</p>
                    </div>
                    <input
                      id="dropzone-file"
                      type="file"
                      className="hidden"
                      multiple
                      onChange={handleFileChange}
                    />
                  </label>
                </div>
                {files.length > 0 && (
                  <div className="space-y-2">
                    <h4 className="text-sm font-semibold">Arquivos selecionados:</h4>
                    <ul className="space-y-2">
                      {files.map((file, index) => (
                        <li key={index} className="flex items-center justify-between p-2 bg-gray-50 rounded">
                          <span className="text-sm">{file.name}</span>
                          <Button
                            variant="ghost"
                            size="sm"
                            onClick={() => {
                              setFiles(prev => prev.filter((_, i) => i !== index));
                            }}
                          >
                            Remover
                          </Button>
                        </li>
                      ))}
                    </ul>
                  </div>
                )}
              </div>
            </CardContent>
          </Card>
        );
      case 4:
        return (
          <Card>
            <CardHeader>
              <CardTitle>Revisão</CardTitle>
              <CardDescription>
                Revise as informações antes de gerar a análise
              </CardDescription>
            </CardHeader>
            <CardContent>
              {analysisResult && (
                <div className="space-y-6">
                  <div className="grid grid-cols-2 gap-4">
                    <div>
                      <Label>Tipo de Imóvel</Label>
                      <p className="font-medium">{analysisResult.dados_imovel.tipo_imovel}</p>
                    </div>
                    <div>
                      <Label>Área Total</Label>
                      <p className="font-medium">{analysisResult.dados_imovel.area_total} m²</p>
                    </div>
                    <div>
                      <Label>Valor Inicial</Label>
                      <p className="font-medium">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(analysisResult.dados_imovel.valor_inicial)}
                      </p>
                    </div>
                    <div>
                      <Label>Valor Atual</Label>
                      <p className="font-medium">
                        {new Intl.NumberFormat('pt-BR', {
                          style: 'currency',
                          currency: 'BRL'
                        }).format(analysisResult.dados_imovel.valor_atual)}
                      </p>
                    </div>
                    <div>
                      <Label>Data do Leilão</Label>
                      <p className="font-medium">
                        {format(new Date(analysisResult.dados_imovel.data_inicio), "PPP", { locale: ptBR })}
                      </p>
                    </div>
                    <div>
                      <Label>Localização</Label>
                      <p className="font-medium">
                        {analysisResult.dados_imovel.bairro}, {analysisResult.dados_imovel.cidade} - {analysisResult.dados_imovel.estado}
                      </p>
                    </div>
                  </div>

                  {analysisResult.recomendacoes && analysisResult.recomendacoes.length > 0 && (
                    <div className="mt-6">
                      <Label>Recomendações da Análise</Label>
                      <ul className="mt-2 space-y-2">
                        {analysisResult.recomendacoes.map((recomendacao, index) => (
                          <li key={index} className="flex items-start space-x-2">
                            <span className="text-primary">•</span>
                            <span>{recomendacao}</span>
                          </li>
                        ))}
                      </ul>
                    </div>
                  )}

                  {files.length > 0 && (
                    <div>
                      <Label>Documentos</Label>
                      <ul className="mt-2 space-y-1">
                        {files.map((file, index) => (
                          <li key={index} className="text-sm">{file.name}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              )}
            </CardContent>
          </Card>
        );
      default:
        return null;
    }
  };

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div className="flex items-center space-x-2">
          {[1, 2, 3, 4].map((step) => (
            <div
              key={step}
              className={`w-8 h-8 rounded-full flex items-center justify-center ${
                currentStep === step
                  ? "bg-primary text-primary-foreground"
                  : "bg-muted"
              }`}
            >
              {step}
            </div>
          ))}
        </div>
      </div>

      {renderStep()}

      <div className="flex justify-between">
        <Button
          variant="outline"
          onClick={() => setCurrentStep(prev => Math.max(1, prev - 1))}
          disabled={currentStep === 1}
        >
          <ArrowLeft className="mr-2 h-4 w-4" />
          Anterior
        </Button>
        <Button
          onClick={() => {
            if (currentStep === 4) {
              handleSubmit();
            } else {
              setCurrentStep(prev => Math.min(4, prev + 1));
            }
          }}
          disabled={loading}
        >
          {currentStep === 4 ? (
            loading ? (
              <>
                <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                Gerando Análise...
              </>
            ) : (
              "Gerar Análise"
            )
          ) : (
            <>
              Próximo
              <ArrowRight className="ml-2 h-4 w-4" />
            </>
          )}
        </Button>
      </div>
    </div>
  );
}
