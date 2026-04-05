import api from "./api";

export const donorService = {
  async list(params = {}) {
    const { data } = await api.get("/donors", { params });
    return data;
  },
  async get(donorId) {
    const { data } = await api.get(`/donors/${donorId}`);
    return data;
  },
  async update(donorId, payload) {
    const { data } = await api.put(`/donors/${donorId}`, payload);
    return data;
  },
};

export const requestService = {
  async create(payload) {
    const { data } = await api.post("/requests", payload);
    return data;
  },
  async list() {
    const { data } = await api.get("/requests");
    return data;
  },
  async get(requestId) {
    const { data } = await api.get(`/requests/${requestId}`);
    return data;
  },
  async matches(requestId) {
    const { data } = await api.get(`/requests/${requestId}/matches`);
    return data;
  },
};

export const notificationService = {
  async generate(payload) {
    const { data } = await api.post("/notifications/generate", payload);
    return data;
  },
  async send(payload) {
    const { data } = await api.post("/notifications/send", payload);
    return data;
  },
  async list() {
    const { data } = await api.get("/notifications");
    return data;
  },
};

export const analyticsService = {
  async summary() {
    const { data } = await api.get("/analytics/summary");
    return data;
  },
};
