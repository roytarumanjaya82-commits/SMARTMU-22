export default {
  async fetch(request) {
    const target = "https://troops-uncertainty-labels-cdt.trycloudflare.com";
    const url = new URL(request.url);
    return Response.redirect(target + url.pathname + url.search, 302);
  }
}
