import { getDefaultConfig } from "@rainbow-me/rainbowkit";
import { http } from "wagmi";
import { sapphire, sapphireTestnet } from "wagmi/chains";

import { createSapphireConfig } from "@oasisprotocol/sapphire-wagmi-v2";

export const config = createSapphireConfig({
  sapphireConfig: {
    replaceProviders: true,
  },
  chains: [sapphireTestnet],
  transports: {
    [sapphireTestnet.id]: http(),
  },
});
