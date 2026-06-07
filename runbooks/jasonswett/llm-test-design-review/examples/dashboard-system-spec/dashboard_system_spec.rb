require "rails_helper"

describe "Dashboard", type: :system do
  describe "scope=active" do
    context "redirect" do
      let!(:order) { create(:order, customer: customer) }
      let!(:customer) { create(:customer) }

      before do
        allow(ENV).to receive(:fetch).and_call_original
        allow(ENV).to receive(:fetch).with("BILLING_API_URL").and_return("https://billing.example.com")
        allow(ENV).to receive(:fetch).with("BILLING_API_TOKEN").and_return("test-token")
        allow_any_instance_of(User).to receive(:can_view?).and_return(true)
        login_as(customer.user)
      end

      it "redirects to the orders page" do
        visit root_path
        expect(page).to have_current_path(orders_path)
      end

      it "shows the order count" do
        controller.instance_variable_set(:@order_count, 5)
        visit dashboard_path
        expect(page).to have_content("5 orders", wait: 3)
      end
    end
  end
end
