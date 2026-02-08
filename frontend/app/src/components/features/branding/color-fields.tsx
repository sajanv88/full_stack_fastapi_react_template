import {
    FormControl,
    FormField,
    FormItem,
    FormLabel,
    FormMessage
} from "@/components/ui/form";
import { Input } from "@/components/ui/input";


/**
 * Utility to convert OKLCH color strings or values to HSL.
 * Handles strings like "oklch(0.708 0.12 200)" or numeric inputs.
 */
export function oklchToHsl(l: number | string, c?: number, h?: number): string {
    let L: number, C: number, H: number;

    // 1. Parse string input if necessary
    if (typeof l === 'string') {
        const match = l.match(/oklch\(([\d.]+)[\s,]+([\d.]+)[\s,]+([\d.]+).*\)/);
        if (!match) return 'hsl(0, 0%, 0%)';
        L = parseFloat(match[1]);
        C = parseFloat(match[2]);
        H = parseFloat(match[3]);
    } else {
        L = l;
        C = c ?? 0;
        H = h ?? 0;
    }

    // 2. OKLCH to OKLAB
    const a = C * Math.cos((H * Math.PI) / 180);
    const aa = C * Math.sin((H * Math.PI) / 180);

    // 3. OKLAB to Linear LMS
    const l_ = L + 0.3963377774 * a + 0.2158037573 * aa;
    const m_ = L - 0.1055613458 * a - 0.0638541728 * aa;
    const s_ = L - 0.0894841775 * a - 1.291485548 * aa;

    const l_lin = l_ ** 3;
    const m_lin = m_ ** 3;
    const s_lin = s_ ** 3;

    // 4. Linear LMS to Linear sRGB
    let r_lin = +4.0767416621 * l_lin - 3.3077115913 * m_lin + 0.2309699292 * s_lin;
    let g_lin = -1.2684380046 * l_lin + 2.6097574011 * m_lin - 0.3413193965 * s_lin;
    let b_lin = -0.0041960863 * l_lin - 0.7034186147 * m_lin + 1.707614701 * s_lin;

    // 5. Linear sRGB to sRGB (standard gamma correction)
    const rev = (c: number) => (c <= 0.0031308 ? 12.92 * c : 1.055 * Math.pow(c, 1 / 2.4) - 0.055);
    const r = Math.min(255, Math.max(0, rev(r_lin) * 255));
    const g = Math.min(255, Math.max(0, rev(g_lin) * 255));
    const b = Math.min(255, Math.max(0, rev(b_lin) * 255));

    // 6. RGB to HSL
    const rn = r / 255, gn = g / 255, bn = b / 255;
    const max = Math.max(rn, gn, bn), min = Math.min(rn, gn, bn);
    let h_hsl = 0, s_hsl = 0, l_hsl = (max + min) / 2;

    if (max !== min) {
        const d = max - min;
        s_hsl = l_hsl > 0.5 ? d / (2 - max - min) : d / (max + min);
        switch (max) {
            case rn: h_hsl = (gn - bn) / d + (gn < bn ? 6 : 0); break;
            case gn: h_hsl = (bn - rn) / d + 2; break;
            case bn: h_hsl = (rn - gn) / d + 4; break;
        }
        h_hsl /= 6;
    }

    return `hsl(${Math.round(h_hsl * 360)}, ${Math.round(s_hsl * 100)}%, ${Math.round(l_hsl * 100)}%)`;
}

/**
 * Convert HSL to hex color format
 */
function hslToHex(hslString: string): string {
    const match = hslString.match(/hsl\((\d+),\s*(\d+)%,\s*(\d+)%\)/);
    if (!match) return '#000000';

    const h = parseInt(match[1]);
    const s = parseInt(match[2]) / 100;
    const l = parseInt(match[3]) / 100;

    const c = (1 - Math.abs(2 * l - 1)) * s;
    const x = c * (1 - Math.abs(((h / 60) % 2) - 1));
    const m = l - c / 2;

    let r = 0, g = 0, b = 0;
    if (h < 60) { r = c; g = x; b = 0; }
    else if (h < 120) { r = x; g = c; b = 0; }
    else if (h < 180) { r = 0; g = c; b = x; }
    else if (h < 240) { r = 0; g = x; b = c; }
    else if (h < 300) { r = x; g = 0; b = c; }
    else { r = c; g = 0; b = x; }

    const toHex = (n: number) => {
        const hex = Math.round((n + m) * 255).toString(16);
        return hex.length === 1 ? '0' + hex : hex;
    };

    return `#${toHex(r)}${toHex(g)}${toHex(b)}`;
}

/**
 * Convert hex color to OKLCH
 */
function hexToOklch(hex: string): string {
    const r = parseInt(hex.slice(1, 3), 16) / 255;
    const g = parseInt(hex.slice(3, 5), 16) / 255;
    const b = parseInt(hex.slice(5, 7), 16) / 255;

    // sRGB to Linear sRGB
    const toLinear = (c: number) => c <= 0.04045 ? c / 12.92 : Math.pow((c + 0.055) / 1.055, 2.4);
    const r_lin = toLinear(r);
    const g_lin = toLinear(g);
    const b_lin = toLinear(b);

    // Linear sRGB to Linear LMS
    const l_lin = 0.4122214708 * r_lin + 0.5363325363 * g_lin + 0.0514459929 * b_lin;
    const m_lin = 0.2119034982 * r_lin + 0.6806995451 * g_lin + 0.1073969566 * b_lin;
    const s_lin = 0.0883024619 * r_lin + 0.2817188376 * g_lin + 0.6299787005 * b_lin;

    // Linear LMS to OKLAB
    const l_ = Math.cbrt(l_lin);
    const m_ = Math.cbrt(m_lin);
    const s_ = Math.cbrt(s_lin);

    const L = 0.2104542553 * l_ + 0.793617785 * m_ - 0.0040720468 * s_;
    const a = 1.9779984951 * l_ - 2.428592205 * m_ + 0.4505937099 * s_;
    const aa = 0.0259040371 * l_ + 0.7827717662 * m_ - 0.808675766 * s_;

    // OKLAB to OKLCH
    const C = Math.sqrt(a * a + aa * aa);
    let H = Math.atan2(aa, a) * (180 / Math.PI);
    if (H < 0) H += 360;

    return `${L.toFixed(3)} ${C.toFixed(3)} ${H.toFixed(2)}`;
}

export default function ColorField({
    control,
    name,
    label
}: {
    control: any;
    name: any;
    label: string;
}) {
    return (
        <FormField
            control={control}
            name={name}
            render={({ field }) => {
                const hslColor = field.value ? oklchToHsl(field.value) : 'hsl(0, 0%, 0%)';
                const hexColor = hslToHex(hslColor);

                const handleColorChange = (e: React.ChangeEvent<HTMLInputElement>) => {
                    const hex = e.target.value;
                    const oklch = `oklch(${hexToOklch(hex)})`;
                    console.log("Selected color in OKLCH:", oklch);
                    field.onChange(oklch);
                };

                return (
                    <FormItem>
                        <FormLabel className="text-sm">{label}</FormLabel>
                        <FormControl>
                            <div className="flex items-center space-x-2">
                                <Input
                                    placeholder="OKLCH value (e.g., 1 0 0)"
                                    {...field}
                                    className="flex-1"
                                />
                                <input
                                    type="color"
                                    value={hexColor}
                                    onChange={handleColorChange}
                                    className="w-10 h-10 rounded border cursor-pointer"
                                />

                            </div>
                        </FormControl>
                        <FormMessage />
                    </FormItem>
                );
            }}
        />
    );
}