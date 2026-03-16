/**
 * Generic HTTP request function.
 * Handles network errors, non-200 status, JSON parse failures,
 * and GraphQL-style { errors } payloads.
 *
 * @param {object} options
 * @param {string} options.url - Full URL to send the request to
 * @param {string} [options.method="GET"] - HTTP method (GET, POST, etc.)
 * @param {object} [options.body] - Request body, will be JSON.stringify'd
 * @param {object} [options.headers] - Additional headers to merge in
 * @param {Array<{key: string, value: string}>} [options.params] - Query params appended to the URL
 * @param {string} [options.responseType="json"] - Response type: "json" or "text"
 * @returns {Promise<{success: boolean, status?: number, data?: object, error?: string}>}
 */
export async function sendRequest({
    url,
    method = "GET",
    body,
    headers = {},
    params = [],
    responseType = "json" })
{
  const queryString = params.length
    ? "?" + params.map(p => `${encodeURIComponent(p.key)}=${encodeURIComponent(p.value)}`).join("&")
    : "";

  const fetchOptions = {
    method,
    headers: {
      ...(body !== undefined ? { "Content-Type": "application/json" } : {}),
      ...headers
    },
    ...(body !== undefined ? { body: JSON.stringify(body) } : {})
  };

  let response;
  try {
    response = await fetch(`${url}${queryString}`, fetchOptions);
  } catch (networkErr) {
    return { success: false, error: `Network error: ${networkErr.message}` };
  }

  const status = response.status;
  let data;
  try {
    data = responseType === "text" ? await response.text() : await response.json();
  } catch (parseErr) {
    return { success: false, status, error: `Failed to parse response: ${parseErr.message}` };
  }

  if (status !== 200) {
    return { success: false, status, error: `HTTP ${status}`, data };
  }

  if (responseType === "json" && data?.errors) {
    return { success: false, status, error: data.errors.map(e => e.message).join("; "), data };
  }

  return { success: true, status, data };
}
