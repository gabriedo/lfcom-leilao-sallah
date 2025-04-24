import { useEffect } from "react";

export default function Partners() {
  const banks = [
    {
      name: "Caixa Econômica Federal",
      logo: "/assets/images/banks/caixa.png",
      className: "translate-y-[10px]"
    },
    {
      name: "Banco do Brasil",
      logo: "/assets/images/banks/bb.png",
      className: "translate-y-[10px]"
    },
    {
      name: "Santander",
      logo: "/assets/images/banks/santander.png",
      className: "translate-y-[10px]"
    },
    {
      name: "Itaú",
      logo: "/assets/images/banks/itau.png",
      className: "scale-50 translate-y-[-25px]"
    },
    {
      name: "Bradesco",
      logo: "/assets/images/banks/bradesco.png",
      className: ""
    },
    {
      name: "Inter",
      logo: "/assets/images/banks/inter.png",
      className: ""
    },
    {
      name: "Banco Pan",
      logo: "/assets/images/banks/pan.png",
      className: "translate-y-[-5px]"
    }
  ];

  // Duplicar os bancos para criar um efeito de loop infinito
  const duplicatedBanks = [...banks, ...banks, ...banks];

  return (
    <section className="py-12 md:py-16 lg:py-20">
      <div className="container mx-auto px-4 md:px-6 lg:px-8">
        <div className="text-center mb-10 md:mb-12 lg:mb-16 max-w-3xl mx-auto">
          <h3 className="text-3xl md:text-4xl lg:text-5xl font-bold text-gray-900 mb-4 md:mb-6">
            Grandes Vendedores
          </h3>
          <p className="text-lg md:text-xl lg:text-2xl text-gray-600 leading-relaxed">
            Consulte imóveis dos maiores vendedores do Brasil
          </p>
        </div>
        
        <div className="relative w-full overflow-hidden">
          <style>
            {`
              @keyframes scroll {
                0% {
                  transform: translateX(0);
                }
                100% {
                  transform: translateX(calc(-100% / 3));
                }
              }
              
              .scroll-container {
                display: flex;
                width: 300%;
                animation: scroll 30s linear infinite;
              }
              
              .scroll-container:hover {
                animation-play-state: paused;
              }
            `}
          </style>
          
          <div className="scroll-container">
            {duplicatedBanks.map((bank, index) => (
              <div 
                key={index} 
                className="flex-none w-[100px] md:w-[120px] lg:w-[140px] px-4 md:px-5 lg:px-6 opacity-75 hover:opacity-100 transition-opacity duration-300"
              >
                <img
                  src={bank.logo}
                  alt={bank.name}
                  className={`w-full h-auto object-contain ${bank.className}`}
                />
              </div>
            ))}
          </div>
        </div>
      </div>
    </section>
  );
}
