require "rails_helper"

RSpec.describe described_class do
  describe "POST /orders" do
    it "works" do
      post orders_path, params: { sku: "ABC-1", qty: 2 }
      order = Order.last
      expect(response).to be_successful
      expect(order.sku).to eq("ABC-1")
    end

    it "charges the customer" do
      gateway = instance_double(PaymentGateway, charge: true)
      allow(PaymentGateway).to receive(:new).and_return(gateway)

      post orders_path, params: { sku: "ABC-1", qty: 2 }

      expect(gateway).to have_received(:charge).with(amount: 1998)
    end
  end
end
