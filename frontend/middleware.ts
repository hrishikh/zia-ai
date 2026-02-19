import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

export function middleware(_request: NextRequest) {
    // Auth is handled client-side by AuthContext.
    // Backend uses in-body refresh tokens, not httpOnly cookies,
    // so there is no server-side cookie to check here.
    return NextResponse.next();
}

export const config = {
    matcher: ["/((?!_next/static|_next/image|favicon.ico|fonts).*)"],
};

