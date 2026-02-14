export interface Integration {
  id: string;
  provider: string;
  is_connected: boolean;
  config: any;
}
