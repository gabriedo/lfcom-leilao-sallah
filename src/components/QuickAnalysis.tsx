import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Skeleton } from "@/components/ui/skeleton";
import { formatCurrency } from "@/lib/utils";

interface QuickAnalysisProps {
  data: {
    tipo_leilao: string;
    valor_inicial: number;
    valor_atual: number;
    data_inicio: string;
    data_fim: string;
    documentos: string[];
  };
  isLoading?: boolean;
}

export default function QuickAnalysis({ data, isLoading = false }: QuickAnalysisProps) {
  if (isLoading) {
    return (
      <div className="space-y-6">
        <div className="flex items-center justify-between">
          <Skeleton className="h-8 w-48" />
          <Skeleton className="h-6 w-24" />
        </div>
        
        <div className="grid gap-4 md:grid-cols-2">
          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-24" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
            </CardContent>
          </Card>

          <Card>
            <CardHeader>
              <Skeleton className="h-6 w-24" />
            </CardHeader>
            <CardContent>
              <div className="space-y-2">
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
                <div className="flex justify-between">
                  <Skeleton className="h-4 w-24" />
                  <Skeleton className="h-4 w-32" />
                </div>
              </div>
            </CardContent>
          </Card>
        </div>
        
        <div className="space-y-4">
          <Skeleton className="h-6 w-36" />
          <div className="grid gap-4">
            {[1, 2, 3].map((i) => (
              <Skeleton key={i} className="h-6 w-full" />
            ))}
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <h2 className="text-2xl font-bold">Análise Rápida</h2>
        <Badge variant="outline" className="text-sm">
          {data.tipo_leilao}
        </Badge>
      </div>
      
      <div className="grid gap-4 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>Valores</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Valor Inicial:</span>
                <span className="font-medium">
                  {!data.valor_inicial || isNaN(data.valor_inicial) ? "Não informado" : formatCurrency(data.valor_inicial)}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Valor Atual:</span>
                <span className="font-medium">
                  {!data.valor_atual || isNaN(data.valor_atual) ? "Não informado" : formatCurrency(data.valor_atual)}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>Datas</CardTitle>
          </CardHeader>
          <CardContent>
            <div className="space-y-2">
              <div className="flex justify-between">
                <span className="text-muted-foreground">Início:</span>
                <span className="font-medium">
                  {!data.data_inicio ? "Não informado" : new Date(data.data_inicio).toLocaleDateString()}
                </span>
              </div>
              <div className="flex justify-between">
                <span className="text-muted-foreground">Fim:</span>
                <span className="font-medium">
                  {!data.data_fim ? "Não informado" : new Date(data.data_fim).toLocaleDateString()}
                </span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
      
      <div className="space-y-4">
        <h3 className="text-lg font-semibold">Pontos de Atenção</h3>
        <div className="grid gap-4">
          {data?.documentos ? (
            data.documentos.map((doc: string, index: number) => (
              <Badge key={index} variant="secondary" className="text-sm">
                {doc}
              </Badge>
            ))
          ) : (
            <p className="text-sm text-gray-500">Nenhum documento encontrado</p>
          )}
        </div>
      </div>
    </div>
  );
} 