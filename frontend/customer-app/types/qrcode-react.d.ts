declare module "qrcode.react" {
  import * as React from "react";

  export interface QRCodeProps {
    value: string;
    size?: number;
    className?: string;
    level?: "L" | "M" | "Q" | "H";
    includeMargin?: boolean;
  }

  export const QRCode: React.FC<QRCodeProps>;
  export default QRCode;
}
