export declare const useAuthStore: import("pinia").StoreDefinition<"auth", {
    token: string;
    username: string;
}, {
    isLoggedIn: (state: {
        token: string;
        username: string;
    } & import("pinia").PiniaCustomStateProperties<{
        token: string;
        username: string;
    }>) => boolean;
}, {
    login(username: string, password: string): Promise<any>;
    logout(): void;
    changePassword(oldPassword: string, newPassword: string): Promise<void>;
}>;
//# sourceMappingURL=auth.d.ts.map