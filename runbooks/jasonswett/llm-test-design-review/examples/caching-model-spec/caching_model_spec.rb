require "rails_helper"

describe Order do
  describe "#total" do
    it "caches the result" do
      order = create(:order, :with_line_items)
      order.total
      expect(Rails.cache.read("order/#{order.id}/total")).not_to be_nil
    end
  end

  describe "status display" do
    it "shows the finished status" do
      task = create(:task)
      task.update!(json_output: { "summary" => { "ok" => true } }.to_json)
      expect(task.reload.display_status).to eq("Finished")
    end
  end
end
