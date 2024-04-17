customElements.whenDefined("hui-plant-status-card").then(() => {
  const plantCard = customElements.get("hui-plant-status-card");
  plantCard.prototype.setConfig = function(config) { this._config = config; }
})

customElements.whenDefined("hui-plant-status-card-editor").then(() => {
  const plantCardEditor = customElements.get("hui-plant-status-card-editor");
  plantCardEditor.prototype.firstUpdated = function () {
    const form = this.shadowRoot.querySelector("ha-form");
    const schema = form.schema;
    schema[0].selector = { entity: {filter: [{domain: "plant"}, {device_class: "plant"}]}};
  }
})