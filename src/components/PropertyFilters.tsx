import React from "react";
import { Button } from "@/components/ui/button";
import { Card, CardContent } from "@/components/ui/card";
import { Label } from "@/components/ui/label";
import { Slider } from "@/components/ui/slider";
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from "@/components/ui/select";
import { Checkbox } from "@/components/ui/checkbox";
import { Accordion, AccordionContent, AccordionItem, AccordionTrigger } from "@/components/ui/accordion";
import { Input } from "@/components/ui/input";
import { PropertyFiltersType } from "@/types/property";

interface PropertyFiltersProps {
  filters: {
    cidade: string;
    estado: string;
    tipo: string;
    modalidade: string;
    min_valor: number;
    max_valor: number;
    quartos: number;
    vagas: number;
    min_area: number;
    max_area: number;
    aceita_financiamento: boolean;
    aceita_FGTS: boolean;
    min_desconto: number;
  };
  setFilters: React.Dispatch<React.SetStateAction<any>>;
  onSearch: () => void;
}

const formatCurrency = (value: number) => {
  return new Intl.NumberFormat('pt-BR', { 
    style: 'currency', 
    currency: 'BRL',
    maximumFractionDigits: 0
  }).format(value);
};

const PropertyFilters: React.FC<PropertyFiltersProps> = ({ filters, setFilters, onSearch }) => {
  const handleInputChange = (field: string, value: any) => {
    setFilters(prev => ({
      ...prev,
      [field]: value
    }));
  };

  return (
    <Card className="w-full border-muted shadow-sm">
      <CardContent className="p-6">
        <Accordion type="single" collapsible defaultValue="basic-filters" className="w-full">
          <AccordionItem value="basic-filters">
            <AccordionTrigger className="text-lg font-semibold">Filtros básicos</AccordionTrigger>
            <AccordionContent>
              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="space-y-2">
                  <Label htmlFor="cidade">Cidade</Label>
                  <Input
                    id="cidade"
                    name="cidade"
                    value={filters.cidade}
                    onChange={(e) => handleInputChange('cidade', e.target.value)}
                    placeholder="Digite a cidade"
                  />
                </div>
                <div className="space-y-2">
                  <Label htmlFor="estado">Estado</Label>
                  <Input
                    id="estado"
                    name="estado"
                    value={filters.estado}
                    onChange={(e) => handleInputChange('estado', e.target.value)}
                    placeholder="Digite o estado"
                  />
                </div>
              </div>

              <div className="space-y-2">
                <Label htmlFor="tipo">Tipo de Imóvel</Label>
                <Select
                  value={filters.tipo}
                  onValueChange={(value) => handleInputChange('tipo', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione o tipo" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Apartamento">Apartamento</SelectItem>
                    <SelectItem value="Casa">Casa</SelectItem>
                    <SelectItem value="Terreno">Terreno</SelectItem>
                    <SelectItem value="Comercial">Comercial</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              <div className="space-y-2">
                <Label htmlFor="modalidade">Modalidade</Label>
                <Select
                  value={filters.modalidade}
                  onValueChange={(value) => handleInputChange('modalidade', value)}
                >
                  <SelectTrigger>
                    <SelectValue placeholder="Selecione a modalidade" />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="Leilão SFI">Leilão SFI</SelectItem>
                    <SelectItem value="Leilão SFI - Edital Único">Leilão SFI - Edital Único</SelectItem>
                    <SelectItem value="Licitação Aberta">Licitação Aberta</SelectItem>
                    <SelectItem value="Venda Online">Venda Online</SelectItem>
                    <SelectItem value="Venda Direta Online">Venda Direta Online</SelectItem>
                  </SelectContent>
                </Select>
              </div>
            </AccordionContent>
          </AccordionItem>

          <AccordionItem value="advanced-filters">
            <AccordionTrigger className="text-lg font-semibold">Filtros avançados</AccordionTrigger>
            <AccordionContent>
              <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mt-4">
                <div className="space-y-2">
                  <Label>Valor Mínimo</Label>
                  <Input
                    type="number"
                    value={filters.min_valor}
                    onChange={(e) => handleInputChange('min_valor', Number(e.target.value))}
                    placeholder="Valor mínimo"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Valor Máximo</Label>
                  <Input
                    type="number"
                    value={filters.max_valor}
                    onChange={(e) => handleInputChange('max_valor', Number(e.target.value))}
                    placeholder="Valor máximo"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Quartos</Label>
                  <Input
                    type="number"
                    value={filters.quartos}
                    onChange={(e) => handleInputChange('quartos', Number(e.target.value))}
                    placeholder="Número de quartos"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Vagas</Label>
                  <Input
                    type="number"
                    value={filters.vagas}
                    onChange={(e) => handleInputChange('vagas', Number(e.target.value))}
                    placeholder="Número de vagas"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Área Mínima (m²)</Label>
                  <Input
                    type="number"
                    value={filters.min_area}
                    onChange={(e) => handleInputChange('min_area', Number(e.target.value))}
                    placeholder="Área mínima"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Área Máxima (m²)</Label>
                  <Input
                    type="number"
                    value={filters.max_area}
                    onChange={(e) => handleInputChange('max_area', Number(e.target.value))}
                    placeholder="Área máxima"
                  />
                </div>

                <div className="space-y-2">
                  <Label>Desconto Mínimo (%)</Label>
                  <Input
                    type="number"
                    value={filters.min_desconto}
                    onChange={(e) => handleInputChange('min_desconto', Number(e.target.value))}
                    placeholder="Desconto mínimo"
                  />
                </div>

                <div className="space-y-2">
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="aceita_financiamento"
                      checked={filters.aceita_financiamento}
                      onCheckedChange={(checked) => handleInputChange('aceita_financiamento', checked)}
                    />
                    <Label htmlFor="aceita_financiamento">Aceita Financiamento</Label>
                  </div>
                  <div className="flex items-center space-x-2">
                    <Checkbox
                      id="aceita_FGTS"
                      checked={filters.aceita_FGTS}
                      onCheckedChange={(checked) => handleInputChange('aceita_FGTS', checked)}
                    />
                    <Label htmlFor="aceita_FGTS">Aceita FGTS</Label>
                  </div>
                </div>
              </div>
            </AccordionContent>
          </AccordionItem>
        </Accordion>

        <div className="flex justify-end mt-4">
          <Button
            className="bg-red-500 hover:bg-red-600 text-white"
            onClick={onSearch}
          >
            Aplicar Filtros
          </Button>
        </div>
      </CardContent>
    </Card>
  );
};

export default PropertyFilters;
