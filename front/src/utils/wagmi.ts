import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { http } from "wagmi";
import { sapphire, sapphireTestnet } from "wagmi/chains";

import { createSapphireConfig } from "@oasisprotocol/sapphire-wagmi-v2";

// export const oasisSapphireTestnet = defineChain({
//   id: 0x5aff,
//   network: "oasis-sapphire-testnet",
//   name: "Oasis Sapphire Testnet",
//   nativeCurrency: { name: "TEST", symbol: "TEST", decimals: 18 },
//   rpcUrls: {
//     default: { http: ["https://testnet.sapphire.oasis.io"] },
//   },
//   testnet: true,
// });

export const config = createSapphireConfig({
  sapphireConfig: {
    replaceProviders: true,
  },
  chains: [sapphireTestnet],
  transports: {
    [sapphireTestnet.id]: http(),
  },
});

// export const config = getDefaultConfig({
//   appName: process.env.NEXT_PUBLIC_SITE_NAME!,
//   projectId: process.env.NEXT_PUBLIC_REOWN_PROJECT_ID!,
//   chains: [sapphireTestnet],
//   multiInjectedProviderDiscovery: false,
//   connectors: [injectedWithSapphire()],
//   transports: {
//     // transports: {
//     //   // [oasisTestnet.id]: http("https://testnet.sapphire.oasis.io"),
//     //   // [sepolia.id]: http(
//     //   //   `https://eth-sepolia.g.alchemy.com/v2/${process.env.NEXT_PUBLIC_ALCHEMY_KEY}`
//     //   // ),
//     // },
//     [sapphire.id]: sapphireHttpTransport(),
//     [sapphireTestnet.id]: sapphireHttpTransport(),
//   },
//   ssr: true,
// });
