import grpc
from app.proto import pricing_service_pb2
from app.proto import pricing_service_pb2_grpc
from app.database import PricingRule
from beanie.exceptions import DocumentNotFound

class PricingService(pricing_service_pb2_grpc.PricingServiceServicer):
    async def CreatePricingRule(self, request, context):
        try:
            rule = PricingRule(
                name=request.name,
                description=request.description,
                conditions=request.conditions,
                actions=request.actions,
                is_active=request.is_active,
                priority=request.priority
            )
            await rule.insert()
            return pricing_service_pb2.PricingRuleResponse(success=True, message="Pricing rule created successfully", rule=rule.dict())
        except Exception as e:
            return pricing_service_pb2.PricingRuleResponse(success=False, message=str(e))

    async def GetPricingRule(self, request, context):
        try:
            rule = await PricingRule.get(request.id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return pricing_service_pb2.PricingRuleResponse()
            return pricing_service_pb2.PricingRuleResponse(success=True, rule=rule.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Pricing rule not found")
            return pricing_service_pb2.PricingRuleResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingRuleResponse()

    async def UpdatePricingRule(self, request, context):
        try:
            rule = await PricingRule.get(request.id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return pricing_service_pb2.PricingRuleResponse()

            update_data = {
                "name": request.name,
                "description": request.description,
                "conditions": request.conditions,
                "actions": request.actions,
                "is_active": request.is_active,
                "priority": request.priority,
            }
            await rule.update({"$set": update_data})
            return pricing_service_pb2.PricingRuleResponse(success=True, message="Pricing rule updated successfully", rule=rule.dict())
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Pricing rule not found")
            return pricing_service_pb2.PricingRuleResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.PricingRuleResponse()

    async def DeletePricingRule(self, request, context):
        try:
            rule = await PricingRule.get(request.id)
            if not rule:
                context.set_code(grpc.StatusCode.NOT_FOUND)
                context.set_details("Pricing rule not found")
                return pricing_service_pb2.DeletePricingRuleResponse()
            await rule.delete()
            return pricing_service_pb2.DeletePricingRuleResponse(success=True, message="Pricing rule deleted successfully")
        except DocumentNotFound:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("Pricing rule not found")
            return pricing_service_pb2.DeletePricingRuleResponse()
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.DeletePricingRuleResponse()

    async def ListPricingRules(self, request, context):
        try:
            rules = await PricingRule.find_all().to_list()
            return pricing_service_pb2.ListPricingRulesResponse(rules=[r.dict() for r in rules])
        except Exception as e:
            context.set_code(grpc.StatusCode.INTERNAL)
            context.set_details(str(e))
            return pricing_service_pb2.ListPricingRulesResponse()
