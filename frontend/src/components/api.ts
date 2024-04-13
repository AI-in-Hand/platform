import { fetchJSON, getServerUrl } from "./utils";

export const fetchMessages = async (sessionId: string, after: string | null = null) => {
  const serverUrl = getServerUrl();
  const fetchMessagesUrl = `${serverUrl}/message/list?session_id=${sessionId}${after ? `&after=${after}` : ""}`;

  const payload = {
    method: "GET",
    headers: {
      "Content-Type": "application/json",
    },
  };

  try {
    const data = await fetchJSON(fetchMessagesUrl, payload);
    if (data && data.status) {
      return data.data;
    } else {
      throw new Error(data.message);
    }
  } catch (error) {
    console.error("Error fetching messages:", error);
    throw error;
  }
};
